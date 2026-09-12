// 文字数ルール検証(creative/department.md「自動チェック」準拠)
// 縦4行まで/横17文字まで(hp/department.mdの banner ルールと同一基準を流用)
function validateTextBlock(text, { maxLines = 4, maxCharsPerLine = 17 } = {}) {
  const lines = String(text || "").split("\n").filter((l) => l.length > 0);
  const errors = [];
  if (lines.length > maxLines) {
    errors.push(`行数超過: ${lines.length}行(最大${maxLines}行)`);
  }
  lines.forEach((line, i) => {
    if (line.length > maxCharsPerLine) {
      errors.push(`${i + 1}行目が${line.length}文字(最大${maxCharsPerLine}文字): "${line}"`);
    }
  });
  return errors;
}

// フィード(カルーセル)のtitle/bodyはCSS側で自然に折り返す長文プロースのため、
// 1行17文字の厳密な制約(バナー的な短文コピー向け)は適用せず、
// 明らかな詰め込み過ぎだけを検知するゆるいチェックにする。
function validateProseBlock(text, { maxTotalChars = 200 } = {}) {
  const t = String(text || "");
  const errors = [];
  if (t.length > maxTotalChars) {
    errors.push(`文字数超過: ${t.length}文字(目安${maxTotalChars}文字以内)`);
  }
  return errors;
}

module.exports = { validateTextBlock, validateProseBlock };
