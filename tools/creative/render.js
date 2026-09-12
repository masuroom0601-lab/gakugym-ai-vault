#!/usr/bin/env node
// 学ジム creative部署: サムネイル/フィード画像レンダラー
// 固定HTML/CSSテンプレート(03_assets/creative-templates/)に、
// spec.jsonのテキスト・パラメータだけを差し込んでPlaywrightでPNG化する。
// 使い方: node render.js <spec.json> <outDir>
const path = require("path");
const fs = require("fs");
const { chromium } = require("playwright");
const { validateTextBlock, validateProseBlock } = require("./validate");

const TEMPLATE_DIR = path.join(__dirname, "..", "..", "03_assets", "creative-templates");

const FEED_TEMPLATES = {
  A: "feed-template-a.html",
  B: "feed-template-b.html",
  C: "feed-template-c.html",
};

function toBase64Utf8(obj) {
  return Buffer.from(JSON.stringify(obj), "utf8").toString("base64");
}

async function shoot(page, templateFile, payload, outPath, viewport) {
  await page.setViewportSize(viewport);
  const b64 = toBase64Utf8(payload);
  const url = "file://" + path.join(TEMPLATE_DIR, templateFile) + "?d=" + encodeURIComponent(b64);
  await page.goto(url);
  await page.waitForSelector('body[data-ready="true"]', { timeout: 8000 }).catch(() => {});
  await page.screenshot({ path: outPath });
}

async function main() {
  const [specPath, outDir] = process.argv.slice(2);
  if (!specPath || !outDir) {
    console.error("usage: node render.js <spec.json> <outDir>");
    process.exit(1);
  }
  const spec = JSON.parse(fs.readFileSync(specPath, "utf8"));
  fs.mkdirSync(outDir, { recursive: true });

  const report = { task_id: spec.task_id, generated: [], errors: [] };
  // ローカル検証時など、事前インストール済みのChromiumパスを明示したい場合に使う
  // (通常のCI実行では `npx playwright install chromium` 後、未設定のままでよい)
  const launchOpts = process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE
    ? { executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE }
    : {};
  const browser = await chromium.launch(launchOpts);
  const page = await browser.newPage();

  try {
    if (spec.thumbnail) {
      const errs = [
        ...validateTextBlock(spec.thumbnail.hype).map((e) => "hype: " + e),
        ...validateTextBlock(spec.thumbnail.headline).map((e) => "headline: " + e),
      ];
      if (errs.length) {
        report.errors.push({ asset: "thumbnail", errors: errs });
      } else {
        const outPath = path.join(outDir, `${spec.task_id}-thumbnail.png`);
        try {
          await shoot(
            page,
            "reel-thumbnail.html",
            { subject: spec.subject, ...spec.thumbnail },
            outPath,
            { width: 1080, height: 1920 }
          );
          report.generated.push(outPath);
        } catch (e) {
          report.errors.push({ asset: "thumbnail", errors: [String(e)] });
        }
      }
    }

    if (spec.feed && Array.isArray(spec.feed.slides)) {
      const templateFile = FEED_TEMPLATES[spec.feed.template];
      if (!templateFile) {
        report.errors.push({
          asset: "feed",
          errors: [`未知のテンプレート指定: ${spec.feed.template}(A/B/Cのいずれかを指定してください)`],
        });
      } else {
        for (let i = 0; i < spec.feed.slides.length; i++) {
          const slide = spec.feed.slides[i];
          const label = `feed-slide-${i + 1}(${slide.role || "content"})`;
          // title/bodyは自然に折り返す長文プロースなので、詰め込み過ぎのみチェック
          const errs = [
            ...validateProseBlock(slide.title, { maxTotalChars: 60 }).map((e) => `${label} title: ` + e),
            ...validateProseBlock(slide.body, { maxTotalChars: 120 }).map((e) => `${label} body: ` + e),
          ];
          if (errs.length) {
            report.errors.push({ asset: label, errors: errs });
            continue;
          }
          const outPath = path.join(outDir, `${spec.task_id}-feed-${String(i + 1).padStart(2, "0")}.png`);
          try {
            await shoot(page, templateFile, slide, outPath, { width: 1080, height: 1350 });
            report.generated.push(outPath);
          } catch (e) {
            report.errors.push({ asset: label, errors: [String(e)] });
          }
        }
      }
    }
  } finally {
    await browser.close();
  }

  const reportPath = path.join(outDir, `${spec.task_id}-render-report.json`);
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
  console.log(JSON.stringify(report, null, 2));
  // レンダリング自体の実行エラー(テンプレート不在等)以外は個々のerrorsに記録し、
  // ワークフロー全体は落とさない(校正担当・秘書担当が report を見て気づける形にする)
  process.exit(0);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
