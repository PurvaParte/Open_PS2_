
import "../App.css";

const concepts = [
  { name: "C++ Fundamentals", score: 86 },
  { name: "Functions", score: 78 },
  { name: "Classes & Objects", score: 64 },
  { name: "Inheritance", score: 42 },
  { name: "Polymorphism", score: 31 },
];

function StudentDashboard() {
  return (
    <div className="app">
      <aside className="sidebar">
        <h2>SkillPath AI</h2>
        <p className="sidebar-label">LEARNING</p>
        <a className="active" href="#dashboard">Dashboard</a>
        <a href="#concepts">Concept Map</a>
        <a href="#assessment">Coding Assessment</a>
        <a href="#viva">Code Viva</a>
        <p className="sidebar-label">REVIEW</p>
        <a href="#trainer">Trainer Dashboard</a>
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <p className="muted">STUDENT WORKSPACE</p>
            <h1>My Learning Dashboard</h1>
          </div>
          <span className="avatar">S</span>
        </header>

        <section className="welcome">
          <p>YOUR PERSONALIZED LEARNING JOURNEY</p>
          <h2>Learn at your own pace.</h2>
          <p>
            Focus on the concepts you need to strengthen,
            one step at a time.
          </p>
        </section>

        <section className="stats">
          <article className="card">
            <p>Overall Mastery</p>
            <h2>60%</h2>
            <span>Across 5 concepts</span>
          </article>
          <article className="card">
            <p>Concepts to Improve</p>
            <h2>2</h2>
            <span>Below 50% mastery</span>
          </article>
          <article className="card">
            <p>Learning Mode</p>
            <h2>Adaptive</h2>
            <span>Based on your progress</span>
          </article>
        </section>

        <section className="content-grid">
          <article className="card mastery-card" id="concepts">
            <h2>Concept Mastery</h2>
            <p className="muted">
              Understand your strengths and knowledge gaps.
            </p>

            {concepts.map((concept) => (
              <div className="concept" key={concept.name}>
                <div className="concept-heading">
                  <span>{concept.name}</span>
                  <strong>{concept.score}%</strong>
                </div>
                <div className="progress">
                  <div
                    className={
                      concept.score < 50
                        ? "progress-fill weak"
                        : "progress-fill"
                    }
                    style={{ width: `${concept.score}%` }}
                  />
                </div>
              </div>
            ))}
          </article>

          <article className="card recommendation" id="assessment">
            <div className="target">✦</div>
            <p className="muted">RECOMMENDED NEXT</p>
            <h2>Strengthen Inheritance</h2>
            <p>
              Practice how a child class inherits properties
              and methods from a parent class.
            </p>
            <div className="reason">
              <strong>Why this topic?</strong>
              <p>
                Your current demo mastery is 42%. Improving
                inheritance can prepare you for polymorphism.
              </p>
            </div>
            <button onClick={() =>
              window.alert("Your coding assessment will be connected next.")
            }>
              Start Practice →
            </button>
          </article>
        </section>

        <footer>
          SkillPath AI · Adaptive Learning and Assessment Portal
        </footer>
      </main>
    </div>
  );
}

export default StudentDashboard;
