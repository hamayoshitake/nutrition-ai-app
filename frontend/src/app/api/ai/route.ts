import { NextRequest, NextResponse } from 'next/server';
import { GraphAI } from 'graphai';

export async function POST(req: NextRequest) {
  try {
    const { prompt } = await req.json();
    if (!prompt) {
      return NextResponse.json({ error: 'No prompt provided' }, { status: 400 });
    }

    // GraphAIのグラフ定義
    const graph = {
      version: 0.5,
      nodes: {
        userInput: {
          value: { text: prompt }
        },
        localAI: {
          // phi4サーバーの /phi4/chat へリクエストするinline agent
          agent: async ({ prompt }: { prompt: string }) => {
            try {
              const res = await fetch("http://localhost:8080/phi4/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text: prompt })
              });
              const data = await res.json();
              console.log('phi4サーバー返答:', data);
              return { text: data.response };
            } catch (e) {
              console.error('phi4サーバー通信エラー:', e);
              return { text: '' };
            }
          },
          inputs: { prompt: ":userInput.text" },
          isResult: true
        }
      }
    };

    // GraphAIでグラフを実行（2つ目の引数を追加）
    const graphai = new GraphAI(graph, {});
    const result = await graphai.run();

    // サーバー側でAI応答をログ出力
    console.log('GraphAI result:', result);

    // localAIノードのtextを返す（nullチェック付き）
    const aiText = result?.localAI && typeof result.localAI === "object" && "text" in result.localAI
      ? (result.localAI as { text: string }).text
      : "";

    return NextResponse.json({ result: aiText });
  } catch (error) {
    return NextResponse.json({ error: String(error) }, { status: 500 });
  }
}
