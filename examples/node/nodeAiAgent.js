const OpenAI = require("openai");
const readline = require("readline");

const openai = new OpenAI({
  apiKey: "",
  baseURL: "http://localhost:8000", // Overwrite base URL
  defaultHeaders: {
    "x-api-key": "value_here", // API_KEY from SEMANTIC-CACHE-API TO PROTECT AGAINST UNAUTHORIZATED REQUEST
  },
});

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

async function askQuestion(question) {
  const response = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
      {
        role: "system",
        content: "You are a helpful AI assistant.",
      },
      {
        role: "user",
        content: question,
      },
    ],
  });

  return response.choices[0].message.content;
}

function prompt() {
  rl.question("You: ", async (input) => {
    if (input.toLowerCase() === "exit") {
      rl.close();
      return;
    }

    const response = await askQuestion(input);
    console.log(`AI: ${response}\n`);
    prompt();
  });
}

console.log("AI Agent - Type your question (or 'exit' to quit):");
prompt();
