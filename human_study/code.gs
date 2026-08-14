/***********************************************************************
 * SNF-Bench axis-specific human study -- Google Apps Script backend.
 *
 * Adapted from the RA-I2V study backend, deliberately reduced. That study
 * asked which clip was better; this one never does. Raters answer only two
 * forced-choice questions, one per failure axis, because the whole point of
 * the benchmark is that "better" conflates the two:
 *
 *   drift  -- which video's background moves more?
 *   decay  -- in which video does the intended motion die out more?
 *
 * Deploy with index.html in the same Apps Script project, paste the generated
 * TRIALS.gs block below, and set SPREADSHEET_ID.
 *
 * Generated pairs come from scripts/make_human_study.py, which samples across
 * small, medium and large metric gaps so agreement is measured over the whole
 * operating range rather than only on obvious cases.
 ***********************************************************************/

const CONFIG = {
  STUDY_TITLE: "Fixed-Camera Video: Background Stability and Motion Persistence",
  APP_VERSION: "snf-bench-axis-study-v1",
  SHEET_NAME: "responses",
  SPREADSHEET_ID: "REPLACE_WITH_SPREADSHEET_ID",
  TRIALS_PER_RATER: 24,        // 12 per axis; about 8 minutes
  ALLOW_TIE: true              // indistinguishable pairs must be answerable
};

const QUESTIONS = {
  drift: "Which video's BACKGROUND moves more? Look at things that should stay " +
         "perfectly still: buildings, banks, rocks, the ground, the horizon. " +
         "Ignore the water, fire, rain or smoke.",
  decay: "In which video does the MOVING CONTENT slow down or stop more by the " +
         "end? Look only at what should be moving: water, fire, rain, smoke. " +
         "Ignore whether the background is stable."
};

const INSTRUCTIONS =
  "You will see two short clips side by side, taken from the same scene " +
  "description. Each question asks about ONE specific thing. Please answer only " +
  "that question -- do not judge which video is better overall, and do not " +
  "consider sharpness, colour or realism. If the two clips genuinely look the " +
  "same for the question asked, choose \"about the same\". Answering honestly " +
  "that a pair is indistinguishable is more useful to us than guessing.";

/* ---- paste the contents of TRIALS.gs here -------------------------------- */
// const TRIALS = [ ... ];
/* ------------------------------------------------------------------------- */

function doGet() {
  return HtmlService.createTemplateFromFile('index')
      .evaluate()
      .setTitle(CONFIG.STUDY_TITLE)
      .addMetaTag('viewport', 'width=device-width, initial-scale=1');
}

function getConfig() {
  return {
    title: CONFIG.STUDY_TITLE,
    instructions: INSTRUCTIONS,
    questions: QUESTIONS,
    allowTie: CONFIG.ALLOW_TIE,
    nTrials: Math.min(CONFIG.TRIALS_PER_RATER, TRIALS.length)
  };
}

/**
 * Trials are served in a per-rater random order, and A/B presentation side is
 * randomised per trial. Without both, a rater who notices that one column is
 * usually the drifting one stops judging the video and starts judging the
 * layout.
 */
function getTrials(raterId) {
  const seed = hashString(raterId || 'anon');
  const order = shuffleWithSeed(TRIALS.map((_, i) => i), seed)
      .slice(0, CONFIG.TRIALS_PER_RATER);
  return order.map(function (i, k) {
    const t = TRIALS[i];
    const flip = ((seed + i) % 2) === 1;
    return {
      trialIndex: k,
      trialId: i,
      axis: t.axis,
      question: QUESTIONS[t.axis],
      left: flip ? t.videoB : t.videoA,
      right: flip ? t.videoA : t.videoB,
      flipped: flip
    };
  });
}

/**
 * Records one response. `choice` is 'left' | 'right' | 'same'; it is resolved
 * back to a system key here, so the client never learns which system is which.
 */
function submitResponse(payload) {
  const ss = SpreadsheetApp.openById(CONFIG.SPREADSHEET_ID);
  let sheet = ss.getSheetByName(CONFIG.SHEET_NAME);
  if (!sheet) {
    sheet = ss.insertSheet(CONFIG.SHEET_NAME);
    sheet.appendRow(['timestamp', 'version', 'raterId', 'trialId', 'axis',
                     'prompt', 'systemA', 'systemB', 'flipped', 'choice',
                     'chosenSystem', 'dwellMs']);
  }
  const t = TRIALS[payload.trialId];
  let chosen = '';
  if (payload.choice === 'same') {
    chosen = 'same';
  } else {
    const pickedLeft = payload.choice === 'left';
    chosen = (pickedLeft !== payload.flipped) ? t.a : t.b;
  }
  sheet.appendRow([new Date(), CONFIG.APP_VERSION, payload.raterId,
                   payload.trialId, t.axis, t.prompt, t.a, t.b,
                   payload.flipped, payload.choice, chosen,
                   payload.dwellMs || '']);
  return { ok: true };
}

/* ---- helpers ------------------------------------------------------------ */
function hashString(s) {
  let h = 0;
  for (let i = 0; i < s.length; i++) { h = (h * 31 + s.charCodeAt(i)) | 0; }
  return Math.abs(h);
}

function shuffleWithSeed(arr, seed) {
  const a = arr.slice();
  let s = seed || 1;
  for (let i = a.length - 1; i > 0; i--) {
    s = (s * 1103515245 + 12345) & 0x7fffffff;
    const j = s % (i + 1);
    const tmp = a[i]; a[i] = a[j]; a[j] = tmp;
  }
  return a;
}
