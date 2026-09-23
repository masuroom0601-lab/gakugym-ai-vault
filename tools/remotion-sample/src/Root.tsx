import "./index.css";
import { Composition } from "remotion";
import { HelloWorld } from "./HelloWorld";
import { Logo } from "./HelloWorld/Logo";
import { CapsHighlight, capsHighlightDurationInFrames } from "./CapsHighlight";
import { Captions } from "./Captions";
import { fromWhisperSegments } from "./Captions/fromWhisperSegments";

const demoCaptions = fromWhisperSegments([
  { text: "早慶MARCH合同の学生団体、CAPS。", start: 0, end: 2.5 },
  { text: "InstagramやTikTokでの学生向け情報発信を中心に活動しています。", start: 2.5, end: 6 },
]);

// Each <Composition> is an entry in the sidebar!

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        // You can take the "id" to render a video:
        // npx remotion render HelloWorld
        id="HelloWorld"
        component={HelloWorld}
        durationInFrames={150}
        fps={30}
        width={1920}
        height={1080}
        // You can override these props for each render:
        // https://www.remotion.dev/docs/parametrized-rendering
        defaultProps={{
          titleText: "Welcome to Remotion",
          titleColor: "#000000",
          logoColor1: "#91EAE4",
          logoColor2: "#86A8E7",
        }}
      />

      <Composition
        id="CapsHighlight"
        component={CapsHighlight}
        durationInFrames={capsHighlightDurationInFrames}
        fps={30}
        width={1080}
        height={1920}
      />

      <Composition
        id="CaptionsDemo"
        component={() => (
          <>
            <div style={{ width: "100%", height: "100%", backgroundColor: "#222" }} />
            <Captions captions={demoCaptions} />
          </>
        )}
        durationInFrames={180}
        fps={30}
        width={1080}
        height={1920}
      />

      {/* Mount any React component to make it show up in the sidebar and work on it individually! */}
      <Composition
        id="OnlyLogo"
        component={Logo}
        durationInFrames={150}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          logoColor1: "#91dAE2",
          logoColor2: "#86A8E7",
        }}
      />
    </>
  );
};
