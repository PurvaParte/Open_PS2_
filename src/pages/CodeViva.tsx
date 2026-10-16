
import { useState } from "react";
import "../App.css";

const questions = [
  {
    question: "Explain the main purpose of your code.",
    hint: "Describe what your program does and its expected output.",
  },
  {
    question: "Explain one important function or method.",
    hint: "Describe its inputs, processing, and result.",
  },
  {
    question: "What happens if the input is invalid?",
    hint: "Explain the behavior and how you would handle the error.",
  },
];

export default function CodeViva() {
  const [answers, setAnswers] = useState(["", "", ""]);
  const [submitted, setSubmitted] = useState(false);

  const answeredCount = answers.filter(
    (answer) => answer.trim().length > 0
  ).length;

  const totalWords = answers.reduce(
    (total, answer) =>
      total +
      (answer.trim() ? answer.trim().split(/\s+/).length : 0),
    0
  );

  function updateAnswer(index: number, value: string) {
    setAnswers((old) =>
      old.map((answer, i) => (i === index ? value : answer))
    );
    setSubmitted(false);
  }

  function submitAnswers() {
    if (answers.some((answer) => !answer.trim())) return;
    setSubmitted(true);
  }

  return (
    <main style={{ padding: 32, maxWidth: 1000, margin: "auto" }}>
      <p className="muted">ASSESSMENT · CODE UNDERSTANDING</p>
      <h1>Code Viva 🎯</h1>
      <p className="muted">
        Explain your solution to demonstrate your programming knowledge.
      </p>

      <section
        className="card"
        style={{ marginTop: 24, background: "#f5f1ff" }}
      >
        <h2>Your Viva Progress</h2>

        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            gap: 16,
            flexWrap: "wrap",
          }}
        >
          <p>
            <strong>{answeredCount}/3</strong> questions answered
          </p>
          <p>
            <strong>{totalWords}</strong> words written
          </p>
        </div>

        <div
          style={{
            height: 9,
            background: "#e3def5",
            borderRadius: 10,
            overflow: "hidden",
          }}
        >
          <div
            style={{
              height: "100%",
              width: `${(answeredCount / questions.length) * 100}%`,
              background: "#6c4bd3",
              transition: "width 0.2s",
            }}
          />
        </div>
      </section>

      {questions.map((item, index) => (
        <section
          className="card"
          key={item.question}
          style={{ marginTop: 18 }}
        >
          <p className="muted">QUESTION {index + 1} OF 3</p>
          <h3>{item.question}</h3>
          <p className="muted">{item.hint}</p>

          <textarea
            value={answers[index]}
            onChange={(event) =>
              updateAnswer(index, event.target.value)
            }
            placeholder="Explain in your own words..."
            rows={5}
            style={{
              width: "100%",
              padding: 14,
              border: "1px solid #dedeea",
              borderRadius: 10,
              resize: "vertical",
              font: "inherit",
              boxSizing: "border-box",
            }}
          />

          <p className="muted">
            {answers[index].trim()
              ? answers[index].trim().split(/\s+/).length
              : 0}{" "}
            words
          </p>
        </section>
      ))}

      <button
        onClick={submitAnswers}
        disabled={answeredCount !== questions.length}
        style={{
          marginTop: 24,
          padding: "14px 24px",
          border: 0,
          borderRadius: 9,
          background:
            answeredCount === questions.length
              ? "#6c4bd3"
              : "#bcb4d4",
          color: "white",
          cursor:
            answeredCount === questions.length
              ? "pointer"
              : "not-allowed",
        }}
      >
        Submit Viva Answers
      </button>

      {answeredCount !== questions.length && (
        <p className="muted">
          Answer all {questions.length} questions to submit.
        </p>
      )}

      {submitted && (
        <section className="card" style={{ marginTop: 20 }}>
          <h2>✅ Viva Submitted</h2>
          <p>
            All three answers are captured in this browser session.
            Your answers have not been sent to the backend or evaluated
            by AI yet.
          </p>
          <p>
            <strong>Total words:</strong> {totalWords}
          </p>
        </section>
      )}
    </main>
  );
}
