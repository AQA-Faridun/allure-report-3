// Allure Report 3 config. Options were checked against the installed `allure` package (see package.json);
// some of them (resolutions, charts) are newer than the docs at allurereport.org.
import { defineConfig } from "allure";

const env = process.env;

// Shared by the awesome report and the standalone dashboard.
const charts = [
  { type: "currentStatus", title: "Current status" },
  { type: "statusDynamics", title: "Status dynamics", limit: 20 },
  { type: "testingPyramid", title: "Testing pyramid", layers: ["api", "web", "e2e"] },
  {
    type: "testResultSeverities",
    title: "Results by severity",
    levels: ["blocker", "critical", "normal", "minor", "trivial"],
  },
  { type: "statusTransitions", title: "Status transitions" },
  { type: "durations", title: "Durations by layer", groupBy: "layer" },
  { type: "durationDynamics", title: "Duration dynamics" },
  { type: "stabilityDistribution", title: "Stability by feature", groupBy: "feature", threshold: 90 },
  { type: "stabilityDistribution", title: "Stability by owner", groupBy: "owner", threshold: 90 },
  { type: "testBaseGrowthDynamics", title: "Test base growth" },
  { type: "statusAgePyramid", title: "Status age" },
];

export default defineConfig({
  name: "Intershop: API + Web autotests",
  output: "./allure-report",
  // Fixed port for `allure open` (make open); without it Allure picks a random free port every time.
  port: env.ALLURE_PORT ?? "2026",

  // History between runs: every report generation appends one line to this file.
  // Keep the file between CI runs (cache/artifact) to get trends, transitions and flaky detection.
  historyPath: "./.allure/history.jsonl",
  historyLimit: 30,
  flakyDetection: { historyDepth: 10 },

  // Shown on the report overview; per-run facts (Python, OS, browser) come from
  // allure-results/environment.properties written by tests/conftest.py.
  variables: {
    "Base URL": env.INTERSHOP_BASE_URL ?? "https://intershop6.skillbox.ru",
    "Run by": env.GITHUB_ACTOR ?? env.USER ?? "local",
    Branch: env.GITHUB_REF_NAME ?? "local",
  },

  // Applied only to tests that do not set these labels themselves.
  defaultLabels: {
    severity: "normal",
    owner: "unassigned",
  },

  // Failure triage. Each failed/broken test lands in the first matching category.
  categories: {
    rules: [
      {
        name: "Known issues (tracked in the bug tracker)",
        matchers: { message: /^SEC-\d+/ },
        groupBy: ["severity"],
      },
      {
        name: "Network / stand unavailable",
        matchers: { statuses: ["broken"], trace: /ConnectError|ConnectTimeout|ReadTimeout|net::ERR_/ },
        groupByMessage: true,
      },
      {
        name: "UI timeouts and locator problems",
        matchers: { statuses: ["failed", "broken"], message: /Locator expected|Timeout \d+ms exceeded/ },
        groupBy: ["layer"],
      },
      {
        name: "Product defects (assertion failed)",
        matchers: { statuses: ["failed"] },
        groupBy: ["layer", "owner"],
        expand: true,
      },
      {
        name: "Test defects (unexpected exception)",
        matchers: { statuses: ["broken"] },
        groupBy: ["layer"],
        groupByMessage: true,
      },
      {
        name: "Flaky tests",
        matchers: { flaky: true },
        groupBy: ["owner"],
      },
    ],
  },

  // Known issues, muted and accepted failures. Matching tests are marked in the report
  // and do not count as failures in the quality gate.
  resolutions: {
    knownIssuesPath: "./.allure/known-issues.json",
    links: {
      tracker: { nameTemplate: "%s", urlTemplate: "https://tracker.example.com/browse/%s" },
    },
    rules: [
      {
        resolution: "issue",
        issue: { id: "SEC-17", type: "tracker" },
        messageRegexp: "^SEC-17",
        comment: "The stand exposes /wp-json/wp/v2/users to guests",
      },
      {
        resolution: "muted",
        messageRegexp: "ConnectError|Connection refused",
        comment: "External dependency of the demo stand is down; muted until it is restored",
      },
    ],
  },

  // `allure run` and `allure quality-gate` exit with code 1 when a rule is broken.
  qualityGate: {
    rules: [
      {
        id: "fail-fast",
        fastFail: true,
        maxFailures: 10,
      },
      {
        id: "release",
        maxFailures: 0,
        minTestsCount: 5,
        successRate: 0.9,
        maxDuration: 120_000,
      },
    ],
  },

  plugins: {
    // Main report: modern UI with tree, charts, timeline, categories, history.
    awesome: {
      options: {
        reportName: "Intershop autotests",
        reportLanguage: "en",
        groupBy: ["epic", "feature", "story"],
        charts,
      },
    },
    // Legacy Allure 2 UI: Suites, Behaviors, Graphs, Timeline and the Environment widget
    // (fed by allure-results/environment.properties).
    allure2: {
      options: { reportName: "Intershop autotests (Allure 2 UI)" },
    },
    // Standalone dashboard with trend charts only.
    dashboard: {
      options: { reportName: "Intershop dashboard", layout: charts },
    },
    // Console summary of failed tests right after the run.
    log: {
      options: { groupBy: "none", filter: ({ status }) => status === "failed" || status === "broken" },
    },
    // allure-report/csv/allure-results.csv: flat export for spreadsheets.
    csv: {
      options: { fileName: "allure-results.csv" },
    },
    // allure-report/testplan/testplan.json: run only failed tests again with ALLURE_TESTPLAN_PATH.
    testplan: {
      options: { fileName: "testplan.json", filter: ({ status }) => status === "failed" || status === "broken" },
    },
  },
});
