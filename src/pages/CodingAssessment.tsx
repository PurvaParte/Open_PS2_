
import { useState } from "react";
import Editor from "@monaco-editor/react";
import "../App.css";

const starterCode: Record<string, string> = {
  python: `# Write your solution here
n = int(input())
print(n * n)
`,
  cpp: `#include <iostream>
using namespace std;

int main() {
    int n;
    cin >> n;
    cout << n * n << endl;
    return 0;
}
`,
  java: `import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        System.out.println(n * n);
        sc.close();
    }
}
`,
};

export default function CodingAssessment() {
  const [language, setLanguage] = useState("python");
  const [code, setCode] = useState(starterCode.python);
  const [result, setResult] = useState("");

  function changeLanguage(value: string) {
    setLanguage(value);
    setCode(starterCode[value]);
    setResult("");
  }

  function submitCode() {
    setResult(
      "Demo submission received. Code execution and test-case evaluation will be connected to the backend."
    );
  }

  return (
    <main style={{ padding: 24, maxWidth: 1200, margin: "auto" }}>
      <p className="muted">ASSESSMENT · PROGRAMMING</p>
      <h1>Coding Assessment</h1>
      <p className="muted">
        Solve the problem, write your code, and submit your solution.
      </p>

      <section
        className="card"
        style={{ marginTop: 20, marginBottom: 20 }}
      >
        <p className="muted">PROBLEM 01 · BEGINNER</p>
        <h2>Calculate the Square</h2>
        <p>
          Write a program that reads an integer <strong>n</strong>
          and prints the square of that number.
        </p>

        <h3>Sample Input</h3>
        <pre
          style={{
            padding: 14,
            background: "#f4f3fa",
            borderRadius: 8,
          }}
        >
          5
        </pre>

        <h3>Sample Output</h3>
        <pre
          style={{
            padding: 14,
            background: "#f4f3fa",
            borderRadius: 8,
          }}
        >
          25
        </pre>
      </section>

      <section className="card" style={{ marginBottom: 20 }}>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            flexWrap: "wrap",
            gap: 12,
          }}
        >
          <h2>Code Editor</h2>

          <select
            value={language}
            onChange={(event) => changeLanguage(event.target.value)}
            style={{
              padding: 10,
              borderRadius: 8,
              border: "1px solid #dedeea",
              font: "inherit",
            }}
          >
            <option value="python">Python</option>
            <option value="cpp">C++</option>
            <option value="java">Java</option>
          </select>
        </div>

        <div
          style={{
            border: "1px solid #dedeea",
            borderRadius: 10,
            overflow: "hidden",
            marginTop: 12,
          }}
        >
          <Editor
            height="350px"
            language={
              language === "cpp"
                ? "cpp"
                : language === "java"
                  ? "java"
                  : "python"
            }
            value={code}
            onChange={(value) => setCode(value ?? "")}
            theme="vs-dark"
            options={{
              minimap: { enabled: false },
              fontSize: 14,
              automaticLayout: true,
              scrollBeyondLastLine: false,
            }}
          />
        </div>

        <div
          style={{
            display: "flex",
            gap: 12,
            marginTop: 18,
            flexWrap: "wrap",
          }}
        >
          <button
            onClick={() => setCode(starterCode[language])}
            style={{
              padding: "12px 20px",
              borderRadius: 8,
              border: "1px solid #dedeea",
              cursor: "pointer",
            }}
          >
            Reset Code
          </button>

          <button
            onClick={submitCode}
            style={{
              padding: "12px 22px",
              border: 0,
              borderRadius: 8,
              background: "#6c4bd3",
              color: "white",
              cursor: "pointer",
            }}
          >
            Submit Solution
          </button>
        </div>
      </section>

      {result && (
        <section className="card" style={{ marginBottom: 20 }}>
          <h2>Submission Status</h2>
          <p>{result}</p>
        </section>
      )}
    </main>
  );
}
