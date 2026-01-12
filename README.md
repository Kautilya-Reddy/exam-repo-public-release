## Local setup:

```bash
git clone git@github.com:Jivraj-18/exam-repo-public-release.git
cd exam-repo-public-release
git submodule update --init --recursive
npm install

npx wrangler dev
# Visit http://localhost:8787

```

## Add New Questions (Create a Pull Request)

To add new questions to an exam, create a pull request with the branch name format: `exam-{roll_no}`

### Steps to Add Questions:

1. **Create a branch with your roll number:**
   ```bash
   git checkout -b exam-YOUR_ROLL_NO
   ```

2. **Add your new question files** to the `src/` directory following the naming convention `q-{question-name}.js`.

3. **Update the exam file** (`src/exam-{name}.js`) to import your new question.

4. **Commit your changes:**
   ```bash
   git add .
   git commit -m "Add new question for exam-YOUR_ROLL_NO"
   ```

5. **Push to the repository:**
   ```bash
   git push origin exam-YOUR_ROLL_NO
   ```

6. **Create a Pull Request:**
   - Go to the repository on GitHub
   - You should see a prompt to create a pull request from your branch
   - Set the title as: `Add Questions: exam-YOUR_ROLL_NO`
   - Submit the pull request

**Important:** Replace `YOUR_ROLL_NO` with your actual roll number (e.g., `exam-B001`, `exam-A123`).

### Example Pull Request

Here's an example of a completed pull request: [PR #1](https://github.com/Jivraj-18/exam-repo-public-release/pull/1) from branch `exam-23f2004759` to `main`

## Add a new exam

To create an exam at `https://exam.sanand.workers.dev/{name}`, add two files:

1. `src/exam-{name}.js`: Defines the questions
2. `src/exam-{name}.info.js`: Defines exam metadata and instructions

### exam-{name}.js

```javascript
import { displayQuestions } from "./utils/display.js";

export async function questions(user, elementMap) {
  const results = [
    // Each import loads a separate question module
    // Can pass user data and weight to each question
    {
      ...(await import("./q-example1.js").then((m) =>
        m.default({
          user, // User data (email, etc) for personalization
          weight: 1, // Optional score weight for this question
        }),
      )),
      help: [html`...`, html`...`], // Optional docs / tutorials shown before the question
    },
  ];

  // 2. Render questions to the DOM
  displayQuestions(results, elementMap);

  // 3. Return question data for scoring
  // Converts [{id: 'q1', answer, weight}, ...] to {q1: {answer, weight}, ...}
  return Object.fromEntries(results.map(({ id, ...rest }) => [id, rest]));
}
```

### exam-{name}.info.js

```javascript
export default {
  // Basic exam settings
  title: "Exam Title",
  start: "2024-11-07T18:30:00+05:30", // When exam becomes available
  hours: 1.0, // Time limit

  // Access control
  admin: (email) => email == "admin@example.com", // Who can administer
  allowed: (email) => email.endsWith(".edu"), // Who can take exam

  // Pre-exam display
  instructions: /* html */ `
    <h1>Instructions</h1>
    <ol>
      <li>Rules...</li>
    </ol>
  `,
};
```



## This is for evals

### Steps we need to execute 

#### clone and create prs.json
gh repo clone Jivraj-18/exam-repo-public-release
cd exam-repo-public-release
gh pr list --limit 500 --json number,headRefName > prs.json

#### extract student submissions 
touch collect_submissions.sh
chmod +x collect_submissions.sh


