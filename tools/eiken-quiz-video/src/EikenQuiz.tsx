import React from "react";
import {
  AbsoluteFill,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import type { QuizProps } from "./Root";

const COLORS = {
  bg: "#ffffff",
  blue: "#2F6FEB",
  red: "#E8323C",
  black: "#141414",
  grey: "#8A8A8A",
  cardBorder: "#E7E7E7",
};

const CountdownRing: React.FC<{
  secondsLeft: number;
  fraction: number; // 1 = full time remaining, 0 = none left
}> = ({ secondsLeft, fraction }) => {
  const size = 220;
  const stroke = 14;
  const r = (size - stroke) / 2;
  const circumference = 2 * Math.PI * r;
  const offset = circumference * (1 - fraction);

  return (
    <div
      style={{
        width: size,
        height: size,
        position: "relative",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <svg width={size} height={size} style={{ position: "absolute", top: 0, left: 0, transform: "rotate(-90deg)" }}>
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          stroke="#EFEFEF"
          strokeWidth={stroke}
          fill="none"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          stroke={COLORS.red}
          strokeWidth={stroke}
          fill="none"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
        />
      </svg>
      <div
        style={{
          fontSize: 92,
          fontWeight: 800,
          color: COLORS.black,
          fontFamily: "'Noto Sans CJK JP', sans-serif",
        }}
      >
        {secondsLeft}
      </div>
    </div>
  );
};

const QuizPhase: React.FC<{ props: QuizProps; quizFrames: number }> = ({
  props,
  quizFrames,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const secondsLeft = Math.max(
    1,
    props.countdownSeconds - Math.floor(frame / fps)
  );
  const fraction = Math.max(0, 1 - frame / quizFrames);

  // fade out just before the end screen takes over
  const opacity = interpolate(
    frame,
    [quizFrames - 10, quizFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  return (
    <AbsoluteFill
      style={{
        backgroundColor: COLORS.bg,
        opacity,
        fontFamily: "'Noto Sans CJK JP', sans-serif",
        alignItems: "center",
      }}
    >
      {/* ヘッドライン */}
      <div style={{ marginTop: 130, textAlign: "center" }}>
        <div
          style={{
            fontSize: 58,
            fontWeight: 700,
            color: COLORS.black,
          }}
        >
          {props.headline1}
        </div>
        <div
          style={{
            width: 420,
            height: 3,
            background: COLORS.black,
            margin: "14px auto 26px",
          }}
        />
        <div style={{ fontSize: 84, fontWeight: 800 }}>
          <span style={{ color: COLORS.blue }}>英検</span>
          <span style={{ color: COLORS.black }}>
            {props.headline2.replace("英検", "")}
          </span>
        </div>
      </div>

      {/* 問題カード */}
      <div
        style={{
          marginTop: 70,
          width: 900,
          background: "#ffffff",
          border: `2px solid ${COLORS.cardBorder}`,
          borderRadius: 28,
          boxShadow: "0 10px 30px rgba(0,0,0,0.08)",
          padding: "40px 48px",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 18, marginBottom: 28 }}>
          <div
            style={{
              background: COLORS.blue,
              color: "#fff",
              fontWeight: 800,
              fontSize: 34,
              padding: "8px 26px",
              borderRadius: 12,
            }}
          >
            英検
          </div>
          <div style={{ color: COLORS.red, fontWeight: 800, fontSize: 40 }}>
            {props.level}
          </div>
        </div>
        <div
          style={{
            fontSize: 44,
            fontWeight: 700,
            color: COLORS.black,
            lineHeight: 1.45,
          }}
        >
          {props.question}
        </div>
      </div>

      {/* 選択肢 */}
      <div style={{ marginTop: 44, width: 900 }}>
        {props.choices.map((choice) => (
          <div
            key={choice}
            style={{
              fontSize: 42,
              fontWeight: 700,
              color: COLORS.black,
              marginBottom: 18,
            }}
          >
            {choice}
          </div>
        ))}
      </div>

      {/* カウントダウン */}
      <div style={{ marginTop: 50 }}>
        <CountdownRing secondsLeft={secondsLeft} fraction={fraction} />
      </div>

      {/* 下部バナー */}
      <div
        style={{
          position: "absolute",
          bottom: 90,
          left: 90,
          right: 90,
          background: "#ffffff",
          border: `2px solid ${COLORS.black}`,
          borderRadius: 60,
          padding: "26px 10px",
          textAlign: "center",
          fontSize: 38,
          fontWeight: 800,
          color: COLORS.black,
        }}
      >
        答えをコメント欄へ！
      </div>
    </AbsoluteFill>
  );
};

const EndPhase: React.FC<{ props: QuizProps; quizFrames: number }> = ({
  props,
  quizFrames,
}) => {
  const frame = useCurrentFrame();
  const localFrame = frame - quizFrames;
  const opacity = interpolate(localFrame, [0, 12], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: COLORS.bg,
        opacity,
        alignItems: "center",
        justifyContent: "center",
        fontFamily: "'Noto Sans CJK JP', sans-serif",
      }}
    >
      <div style={{ textAlign: "center" }}>
        <div
          style={{
            fontSize: 72,
            fontWeight: 800,
            color: COLORS.black,
            lineHeight: 1.5,
          }}
        >
          {props.endScreenText}
        </div>
        <div
          style={{
            width: 260,
            height: 6,
            background: COLORS.red,
            margin: "34px auto 0",
            borderRadius: 3,
          }}
        />
        <div
          style={{
            marginTop: 60,
            fontSize: 36,
            fontWeight: 700,
            color: COLORS.blue,
          }}
        >
          学ジム
        </div>
      </div>
    </AbsoluteFill>
  );
};

export const EikenQuiz: React.FC<QuizProps> = (props) => {
  const { fps } = useVideoConfig();
  const quizFrames = props.countdownSeconds * fps;

  return (
    <AbsoluteFill>
      <QuizPhase props={props} quizFrames={quizFrames} />
      <EndPhase props={props} quizFrames={quizFrames} />
    </AbsoluteFill>
  );
};
