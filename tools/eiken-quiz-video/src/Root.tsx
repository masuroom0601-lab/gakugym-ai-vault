import React from "react";
import { Composition } from "remotion";
import { z } from "zod";
import { EikenQuiz } from "./EikenQuiz";

export const quizPropsSchema = z.object({
  headline1: z.string(),
  headline2: z.string(),
  level: z.string(),
  question: z.string(),
  choices: z.tuple([z.string(), z.string(), z.string(), z.string()]),
  countdownSeconds: z.number().int().positive(),
  endScreenText: z.string(),
});

export type QuizProps = z.infer<typeof quizPropsSchema>;

const defaultProps: QuizProps = {
  headline1: "受験英語10秒で解けないと",
  headline2: "英検キツイ",
  level: "準2級レベル",
  question: "Every student and every teacher ( ___ ) hard worker.",
  choices: ["① are", "② were", "③ is", "④ have"],
  countdownSeconds: 10,
  endScreenText: "答え&解説はキャプションへ！",
};

const FPS = 30;

export const Root: React.FC = () => {
  return (
    <Composition
      id="EikenQuiz"
      component={EikenQuiz}
      durationInFrames={defaultProps.countdownSeconds * FPS + 2 * FPS}
      fps={FPS}
      width={1080}
      height={1920}
      schema={quizPropsSchema}
      defaultProps={defaultProps}
      calculateMetadata={async ({ props }) => {
        return {
          durationInFrames: props.countdownSeconds * FPS + 2 * FPS,
        };
      }}
    />
  );
};
