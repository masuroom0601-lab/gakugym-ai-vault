import { loadDefaultJapaneseParser } from "budoux";

const parser = loadDefaultJapaneseParser();

// Greedily packs BudouX phrases into lines no longer than maxCharsPerLine,
// so a line break never lands mid-word/mid-phrase.
export const wrapJapanese = (text: string, maxCharsPerLine: number): string[] => {
  const phrases = parser.parse(text);
  const lines: string[] = [];
  let current = "";

  for (const phrase of phrases) {
    if (current.length > 0 && current.length + phrase.length > maxCharsPerLine) {
      lines.push(current);
      current = phrase;
    } else {
      current += phrase;
    }
  }
  if (current.length > 0) lines.push(current);

  return lines;
};
