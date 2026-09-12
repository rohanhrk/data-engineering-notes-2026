# AI Fundamentals for Data Engineering

> **Purpose:** Interview-ready and practical notes for a Data Engineer
> who needs to understand AI/ML fundamentals and how AI systems depend
> on data engineering.
>
> **Source:** AI Fundamentals For Data Engineering

------------------------------------------------------------------------

## 1. AI and Data Engineering

### 1.1 AI as a Productivity Multiplier

AI can help Data Engineers complete repetitive engineering work faster,
but the engineer remains responsible for correctness, production
readiness, and operational decisions.

``` mermaid
flowchart LR
    A[Business / Engineering Requirement] --> B[AI Assistant]
    B --> C[SQL / Python / PySpark]
    B --> D[Tests / Documentation]
    B --> E[Debugging Suggestions]
    C --> F[Data Engineer Review]
    D --> F
    E --> F
    F --> G[Production Pipeline]
```

### Practical use cases

-   Generate SQL, Python, and PySpark from natural-language
    requirements.
-   Explain complex queries, Spark jobs, and unfamiliar code.
-   Debug pipeline failures from logs and error messages.
-   Create unit tests, data-quality checks, and sample datasets.
-   Refactor inefficient code and suggest performance improvements.
-   Generate documentation, data dictionaries, and source-to-target
    mappings.

### Example

**Requirement:** Read daily order data from Amazon S3, remove
duplicates, calculate customer-level revenue, and load the result into
Snowflake.

AI can generate:

-   PySpark transformation code
-   Snowflake SQL
-   Airflow DAG structure
-   Data-quality checks
-   Initial documentation

But the Data Engineer must validate:

-   Join and aggregation logic
-   Incremental loading strategy
-   Partitioning and performance
-   Failure recovery and idempotency
-   Security and production readiness

### Common tools mentioned

-   ChatGPT
-   Claude
-   Cursor
-   Antigravity
-   Google Gemini
-   GitHub Copilot

> **Interview point:** AI is an engineering accelerator, not a
> replacement for engineering ownership.

------------------------------------------------------------------------

## 2. Data Engineers Enable Production AI

AI applications depend on reliable, fresh, and governed data.

``` mermaid
flowchart LR
    A[Source Data] --> B[Ingestion]
    B --> C[Cleaning]
    C --> D[Transformation]
    D --> E[Chunking]
    E --> F[Embeddings]
    F --> G[Vector Database]
    G --> H[AI Application / RAG]
    I[Document Changes] --> B
```

### RAG / Enterprise Search example

Suppose an employee asks:

> "What is the company leave policy?"

The data pipeline may need to:

1.  Ingest PDFs, documents, and web pages.
2.  Extract and clean text.
3.  Break documents into chunks.
4.  Generate embeddings.
5.  Store embeddings in a vector database.
6.  Keep the index updated when source documents change.

### Tools mentioned in the source

-   Airflow
-   Spark
-   AWS Glue
-   LangChain
-   LlamaIndex
-   OpenAI embeddings
-   Amazon OpenSearch

> **Key idea:** A production AI system is only as useful as the data
> pipeline that supplies and maintains its data.

------------------------------------------------------------------------

# 3. Artificial Intelligence (AI)

## 3.1 What is AI?

**Artificial Intelligence** is the broad field of building systems that
can perform tasks that normally require human intelligence.

Examples:

-   Decision making
-   Language understanding
-   Image recognition
-   Planning
-   Problem solving
-   Content generation

``` mermaid
flowchart TD
    AI[Artificial Intelligence]
    AI --> Rules[Rules]
    AI --> Search[Search]
    AI --> ML[Machine Learning]
    AI --> DL[Deep Learning]
    AI --> LLM[Large Language Models]
    AI --> Agents[AI Agents]
```

### Example: E-commerce support

For:

> "Where is my order?"

An AI system may:

1.  Understand the question.
2.  Find the customer's order.
3.  Check shipment status.
4.  Decide what information is relevant.
5.  Generate a response.

------------------------------------------------------------------------

# 4. Machine Learning (ML)

## 4.1 What is Machine Learning?

Machine Learning teaches computers to learn patterns from data rather
than following only fixed, pre-programmed rules.

### Traditional programming

``` mermaid
flowchart LR
    A[Rules] --> C[Program]
    B[Input Data] --> C
    C --> D[Output]
```

Example:

``` text
IF email contains "win money"
AND sender is unknown
THEN mark as spam
```

### Machine Learning

``` mermaid
flowchart LR
    A[Input Data X] --> C[ML Algorithm]
    B[Correct Answers / Labels Y] --> C
    C --> D[Learned Model]
    D --> E[Predictions]
```

Instead of explicitly writing every rule:

1.  Provide input data.
2.  Provide correct answers when available.
3.  The algorithm learns patterns.
4.  The resulting mathematical model represents those learned patterns.

------------------------------------------------------------------------

## 4.2 Features, Labels, and Models

Consider house-price prediction.

-   **Features (X):** Size, Bedrooms, Location
-   **Label / Target (Y):** Price
-   **Model:** Mathematical function mapping inputs to an output.

A simplified model can be represented as:

``` text
Price = (w1 × Size) + (w2 × Bedrooms) + (w3 × Location) + bias
```

Where:

-   `w1`, `w2`, `w3` = learned weights
-   `bias` = additional adjustable value

### How training works

``` mermaid
flowchart TD
    A[Start with initial weights] --> B[Make prediction]
    B --> C[Compare with actual value]
    C --> D[Calculate error]
    D --> E[Adjust weights]
    E --> B
    B --> F[Repeat many times]
```

The repeated process of learning from examples and adjusting the model
is called **training**.

------------------------------------------------------------------------

## 4.3 Core ML Terms

  -----------------------------------------------------------------------
  Term                                Meaning
  ----------------------------------- -----------------------------------
  Feature                             Input variable used by a model

  Label / Target                      Expected output variable

  Model                               Mathematical function mapping input
                                      to output

  Training                            Learning patterns from data

  Testing                             Evaluating a model on unseen data

  Overfitting                         Model memorizes training data
                                      instead of learning general
                                      patterns
  -----------------------------------------------------------------------

### Overfitting

``` mermaid
flowchart LR
    A[Training Data] --> B[Model]
    B --> C[Very Good Training Performance]
    B --> D[Poor Generalization on Unseen Data]
```

> **Interview definition:** Overfitting happens when a model learns the
> training data too closely, including patterns that do not generalize
> to unseen data.

------------------------------------------------------------------------

# 5. Types of Machine Learning

``` mermaid
flowchart TD
    ML[Machine Learning]
    ML --> S[Supervised Learning]
    ML --> U[Unsupervised Learning]
    ML --> R[Reinforcement Learning]

    S --> SR[Regression]
    S --> SC[Classification]

    U --> UC[Clustering]
    U --> UA[Anomaly Detection]
    U --> UAR[Association Rules]
```

------------------------------------------------------------------------

## 5.1 Supervised Learning

Supervised learning learns from examples where the correct answer is
known.

### Input

``` text
X = Input features
Y = Correct answer / label
```

``` mermaid
flowchart LR
    A[Features X] --> C[Supervised ML Model]
    B[Known Label Y] --> C
    C --> D[Learned Pattern]
    D --> E[Prediction for New Data]
```

### Example: Customer churn

Training data might contain:

-   Usage
-   Complaints
-   Contract type
-   Churned? → label

For a new customer:

``` text
Usage = Low
Complaints = 6
Contract = Monthly

        ↓

      Model

        ↓

Churn Probability = 91%
```

### Two major supervised-learning problems

#### Regression

Predicts a **number**.

Example:

``` text
House features → Model → House price = ₹85 lakh
```

Algorithms mentioned in the source:

-   Linear Regression
-   Decision Tree Regressor

#### Classification

Predicts a **category**.

Examples:

-   Spam / Not Spam
-   Churn / No Churn

Algorithms mentioned in the source:

-   Random Forest
-   KNN
-   Naive Bayes
-   SVM

### Regression vs Classification

  -----------------------------------------------------------------------
  Aspect                  Regression              Classification
  ----------------------- ----------------------- -----------------------
  Output                  Numeric value           Category

  Example                 House price             Spam / Not Spam

  Source examples         Linear Regression,      Random Forest, KNN,
                          Decision Tree Regressor Naive Bayes, SVM
  -----------------------------------------------------------------------

------------------------------------------------------------------------

# 6. Unsupervised Learning

Unsupervised learning finds patterns when there is no predefined correct
output/label.

``` mermaid
flowchart LR
    A[Customer Data] --> B[Unsupervised Algorithm]
    B --> C[Discover Similar Patterns]
    C --> D[Cluster 1]
    C --> E[Cluster 2]
    D --> F[High Spend / Frequent]
    E --> G[Low Spend / Occasional]
```

The algorithm discovers groups; the business can interpret those groups
later.

For example:

-   Premium customers
-   Regular customers
-   Occasional customers

### Common uses

#### Clustering

Customer segmentation.

#### Anomaly detection

Finding unusual transaction patterns.

#### Association rules

Finding relationships such as:

``` text
Customers buying bread
        ↓
often also buy butter
```

> **Important distinction:** Supervised learning learns from known
> answers; unsupervised learning discovers structure without predefined
> labels.

------------------------------------------------------------------------

# 7. Reinforcement Learning

Reinforcement Learning learns through **actions and feedback**.

Unlike supervised learning, there does not need to be a dataset
containing the correct answer for every situation.

``` mermaid
flowchart LR
    A[Agent] -->|Action| B[Environment]
    B -->|State / Outcome| A
    B -->|Reward / Penalty| A
```

The agent learns:

> Which actions maximize total future reward?

### Example

An AI learns to play a game:

1.  Take an action.
2.  Observe what happens.
3.  Receive reward or penalty.
4.  Adjust future behavior.
5.  Repeat many times.

### Practical use cases

-   Game-playing AI
-   Robot navigation/control
-   Resource allocation
-   Dynamic recommendation strategies
-   Some autonomous-system decision problems

------------------------------------------------------------------------

# 8. Neural Networks

A neural network is a machine-learning model made from connected
computational units called neurons.

### Important components

  -----------------------------------------------------------------------
  Component                           Meaning
  ----------------------------------- -----------------------------------
  Weight                              Represents how important an input
                                      is

  Bias                                Additional adjustable value

  Activation function                 Determines how the calculated
                                      signal moves forward

  Neuron                              One calculation unit

  Hidden layer                        Collection of neurons learning
                                      intermediate patterns

  Neural network                      Many connected neurons/layers
  -----------------------------------------------------------------------

``` mermaid
flowchart LR
    A[Inputs] --> B[Neuron]
    B --> C[Weighted Calculation]
    C --> D[Activation Function]
    D --> E[Output]
```

A larger network connects many such neurons into layers.

------------------------------------------------------------------------

# 9. Deep Learning

Deep Learning uses neural networks containing **multiple layers** to
learn increasingly complex patterns.

``` mermaid
flowchart LR
    A[Input] --> B[Hidden Layer 1]
    B --> C[Hidden Layer 2]
    C --> D[Hidden Layer 3]
    D --> E[...]
    E --> F[Hidden Layer N]
    F --> G[Output]
```

More layers allow the model to learn more complex representations.

## Example: Invoice understanding

An invoice image can be processed through increasingly meaningful
representations:

``` text
Pixels
  ↓
Lines & Shapes
  ↓
Characters
  ↓
Words
  ↓
Fields
  ↓
Invoice Number / Vendor / Total Amount
```

### Where deep learning became important

-   Image recognition
-   Speech recognition
-   Language translation
-   Document understanding
-   Autonomous systems
-   Large Language Models

------------------------------------------------------------------------

# 10. NLP --- Natural Language Processing

**Natural Language Processing (NLP)** is the area of AI focused on
processing, understanding, and generating human language.

### Common language data

-   Emails
-   Documents
-   Chats
-   Reviews
-   Support tickets
-   Contracts
-   Questions

### Example: Sentiment analysis

``` text
"Delivery was fast but the product quality was terrible."
                    ↓
            Language Processing
                    ↓
               Sentiment
                    ↓
                NEGATIVE
```

### NLP use cases

-   Text classification
-   Sentiment analysis
-   Translation
-   Summarization
-   Chatbots

## Evolution of NLP

``` mermaid
flowchart LR
    A[Rule-Based NLP] --> B[Machine Learning NLP]
    B --> C[Deep Learning NLP]
    C --> D[Transformers / LLMs]
```

### Important clarification

NLP is **not simply another layer below Deep Learning**.

Think of it this way:

``` mermaid
flowchart TD
    A[NLP = Language Problem Domain]
    B[Machine Learning = Technique]
    C[Deep Learning = Technique]
    D[Transformers / LLMs = Model Architecture / Family]

    B --> A
    C --> A
    D --> A
```

NLP describes the **problem domain: language**.

Machine Learning and Deep Learning are techniques that can be used to
solve NLP problems.

------------------------------------------------------------------------

# 11. Generative AI

Generative AI is a category of AI designed to generate new content based
on patterns learned from large amounts of data.

### It can generate

-   Text
-   Code
-   Images
-   Audio
-   Video

## Generative AI vs Traditional ML

``` mermaid
flowchart LR
    A[Traditional ML] --> B[Predict]
    B --> C["Will customer churn? → 82%"]

    D[Generative AI] --> E[Create]
    E --> F["Generate SQL / Summarize / Answer / Create Image"]
```

### Data Engineering Copilot example

Requirement:

> "Write a PySpark job that reads orders from S3, removes duplicates,
> and calculates daily revenue."

``` mermaid
flowchart LR
    A[Natural Language Requirement] --> B[LLM]
    B --> C[Generated PySpark]
    C --> D[Data Engineer Review]
    D --> E[Production Pipeline]
```

> **Key idea:** Traditional ML is commonly used to predict outcomes;
> Generative AI creates new content.

------------------------------------------------------------------------

# 12. Large Language Models (LLMs)

## 12.1 What is an LLM?

An LLM is a deep-learning model designed using the **Transformer
architecture**, trained on massive amounts of text/code to learn
language patterns and predict the next token.

At its core, an LLM performs **next-token prediction**.

### Example

Prompt:

``` text
"The capital of France is"
```

The model might calculate probabilities such as:

``` text
Paris   → 96%
London  → 1%
Berlin  → 0.5%
Others  → remaining probability
```

The model selects a token and then predicts the next token again.

``` mermaid
flowchart LR
    A[Prompt] --> B[Predict Next Token]
    B --> C[Add Selected Token to Context]
    C --> B
    B --> D[Complete Response]
```

### Why "Large"?

Modern LLMs are trained using:

-   Massive datasets
-   Billions of model parameters
-   Large GPU/accelerator clusters
-   Deep neural-network architectures

An LLM is fundamentally a powerful next-token prediction model that has
learned language patterns, knowledge, and reasoning behaviours from
enormous amounts of data.

------------------------------------------------------------------------

# 13. LLM Model Types

The source groups popular models into two broad categories.

## Closed / Proprietary

Examples mentioned:

-   GPT
-   Claude
-   Gemini
-   Grok
-   Amazon Nova

Typical access pattern:

``` mermaid
flowchart LR
    A[Your Application] --> B[API]
    B --> C[Provider's Model]
```

The provider keeps the model weights private. You normally do not
download and host the actual model yourself.

## Open / Open-weight focused

Examples mentioned:

-   Llama
-   DeepSeek
-   Qwen
-   Mistral

Typical pattern:

``` mermaid
flowchart LR
    A[Model Weights] --> B[Download]
    B --> C[Your GPU / Cloud]
    C --> D[Fine-tune]
    D --> E[Deploy]
```

This can allow an enterprise to run a model on its own infrastructure
instead of calling an external LLM API.

------------------------------------------------------------------------

# 14. Parameters

When someone says:

> "This is a 100B parameter LLM."

It means the neural network contains roughly **100 billion learned
numerical values**.

These parameters control how information flows through the neural
network.

The source notes that most parameters are weights, along with some
biases and other learned values.

### Why more parameters?

The main advantage described is greater **model capacity** --- the
ability to learn and represent more complex patterns.

> **Do not equate parameter count directly with model quality.**
> Parameter count describes scale/capacity; the source does not state
> that it alone determines model quality.

------------------------------------------------------------------------

# 15. Core LLM Terms

## 15.1 Token

LLMs do not directly process normal words as whole concepts. Text is
broken into smaller units called **tokens**.

The source gives the rough rule:

> **4 English characters ≈ 1 token**

This is only an approximation.

A token can be:

-   A complete word
-   Part of a word
-   A character
-   Punctuation
-   A word together with preceding space

### Example

``` text
"Data Engineering is amazing"

          ↓ Tokenizer

"Data" | " Engineering" | " is" | " amazing"
```

``` mermaid
flowchart LR
    A[Text] --> B[Tokenizer]
    B --> C[Tokens]
```

------------------------------------------------------------------------

# 16. Embeddings

A neural network needs numerical representations rather than raw words.

An **embedding** converts a token into a numerical vector.

Example:

``` text
database → [0.21, -0.45, 0.81, ...]
```

The important idea is not any individual number. It is the
**relationship between vectors**.

For example:

``` text
database ───── close ───── table

database ───────────── far ───────────── banana
```

Because "database" and "table" are semantically related, their learned
vectors tend to be closer in the model's multidimensional space.

### Conceptual pipeline

``` mermaid
flowchart LR
    A[Token] --> B[Embedding Layer]
    B --> C[Numerical Vector]
    C --> D[Neural Network]
```

> **Interview definition:** An embedding is a numerical vector
> representation that allows language information to be processed
> mathematically and captures useful relationships between tokens.

------------------------------------------------------------------------

# 17. Prompt, System Prompt, Context, and User Prompt

## Prompt

The prompt is the input/instructions provided to the model.

But an LLM application can conceptually combine multiple types of
information.

### System Prompt

Defines model/application behaviour.

Think:

> Who are you? How should you behave? What rules should you follow?

Usually written by the application developer.

### Context

Information supplied to help the model answer.

Context can include:

-   Previous conversation
-   Retrieved documents from RAG
-   Customer/account information
-   Tool outputs
-   Application-specific data

Think:

> What information does the model currently have available?

### User Prompt

What the user actually asks.

Example:

``` text
"Why did my card payment fail?"
```

### Conceptual structure

``` mermaid
flowchart TD
    A[System Prompt] --> D[Effective Model Input]
    B[Context] --> D
    C[User Prompt] --> D
    D --> E[LLM]
    E --> F[Response]
```

------------------------------------------------------------------------

# 18. Temperature

Temperature controls how strongly generation prefers high-probability
token choices.

Suppose:

``` text
Prompt:
"Data engineering is..."
```

The model may estimate:

``` text
important   → 35%
challenging → 25%
interesting → 20%
essential   → 12%
fun         → 8%
```

### Low temperature

Example:

``` text
temperature = 0.1
```

The model strongly prefers high-probability choices.

Possible style:

> Data engineering is an important part of building reliable data
> platforms.

### Higher temperature

Example:

``` text
temperature = 0.9
```

Lower-probability alternatives get more opportunity to be selected.

Possible style:

> Data engineering is the invisible plumbing that keeps modern AI
> systems alive.

### Practical mental model

``` mermaid
flowchart LR
    A[Lower Temperature] --> B[More Deterministic / Conservative]
    C[Higher Temperature] --> D[More Varied / Creative]
```

> **Important:** Temperature affects token selection behaviour; it does
> not add knowledge to the model.

------------------------------------------------------------------------

# 19. Context Window

The **context** is everything the model can currently see while
generating its response.

The source gives GPT-5 as an example with a 400,000-token context window
and up to 128,000 reasoning/output tokens, with the remaining capacity
available for input/context under the described conceptual allocation.

### Why context matters

A model can only work with the information available within its context
window.

``` mermaid
flowchart LR
    A[System Instructions] --> D[Context Window]
    B[User Prompt] --> D
    C[Retrieved / Previous Information] --> D
    D --> E[LLM]
    E --> F[Output]
```

------------------------------------------------------------------------

# 20. How an LLM Processes a Prompt

Example:

> "Explain Apache Spark in simple terms."

## Step 1 --- Tokenization

``` text
Prompt
  ↓
Tokenizer
  ↓
Tokens / Token IDs
```

The input is broken into tokens.

## Step 2 --- Embeddings

``` text
Tokens
  ↓
Embedding Layer
  ↓
Numerical Representations
```

Tokens become vectors.

## Step 3 --- Transformer Layers

The vectors pass through many Transformer blocks.

``` mermaid
flowchart TD
    A[Token Embeddings] --> B[Transformer Block 1]
    B --> C[Transformer Block 2]
    C --> D[Transformer Block 3]
    D --> E[...]
    E --> F[Transformer Block N]
```

Inside these layers, **attention** helps the model understand
relationships between tokens.

Example:

``` text
"Spark distributes data across multiple machines."

Spark
  ↕
distributes
  ↕
data
  ↕
machines
```

## Step 4 --- Next-token prediction

For:

``` text
"Apache Spark is a"
```

The model may calculate:

``` text
distributed → 45%
data        → 25%
framework   → 20%
database    → 2%
```

One token is selected.

## Step 5 --- Repeat

``` text
Apache Spark is a
        ↓
Apache Spark is a distributed
        ↓
Apache Spark is a distributed processing
        ↓
Apache Spark is a distributed processing framework
```

This continues until the response is complete.

------------------------------------------------------------------------

# 21. Transformer Architecture

The source describes modern GPT-style LLMs as using **decoder-only
Transformer blocks**.

Each block mainly contains:

1.  **Masked Self-Attention**
2.  **Feed Forward Network**

``` mermaid
flowchart TD
    A[Input Token Representations] --> B[Masked Self-Attention]
    B --> C[Feed Forward Network]
    C --> D[Output Representations]
    D --> E[Next Transformer Block]
```

## Masked Self-Attention

Each token can look at earlier relevant tokens to understand context.

Example:

``` text
"The Glue job failed due to schema mismatch."
```

The token **"mismatch"** can pay more attention to:

-   Schema
-   Failed
-   Glue job

This helps the model form the interpretation:

> The failure is related to a schema mismatch.

## Feed Forward Network

After attention gathers contextual information, the feed-forward network
further refines that representation.

Conceptually:

``` text
Attention
   ↓
Contextual Understanding
   ↓
Feed Forward Network
   ↓
Refined Representation
```

------------------------------------------------------------------------

# 22. End-to-End LLM Architecture

A simplified view of the complete workflow:

``` mermaid
flowchart TD
    A[User Input / Prompt]
    A --> B[Tokenization]
    B --> C[Token IDs]
    C --> D[Embeddings + Position Information]
    D --> E[Transformer Blocks]

    E --> E1[Masked Self-Attention]
    E1 --> E2[Feed Forward Network]
    E2 --> E3[Repeated Transformer Blocks]

    E3 --> F[Next-Token Probability Distribution]
    F --> G[Select Next Token]
    G --> H[Add Token to Context]
    H --> F

    F --> I[Completed Response]
```

### Key flow to remember

``` text
Prompt
  ↓
Tokenization
  ↓
Token IDs
  ↓
Embeddings + Position Information
  ↓
Transformer Blocks
  ↓
Attention + Feed Forward
  ↓
Next-token probabilities
  ↓
Select token
  ↓
Repeat
  ↓
Response
```

------------------------------------------------------------------------

# 23. AI Fundamentals Hierarchy

Use this mental model to connect the major concepts:

``` mermaid
flowchart TD
    AI[Artificial Intelligence]
    AI --> ML[Machine Learning]
    ML --> NN[Neural Networks]
    NN --> DL[Deep Learning]
    DL --> NLP[NLP Applications]
    DL --> LLM[LLMs]
    LLM --> GenAI[Generative AI Applications]

    NLP --> T[Transformers / LLMs]
    GenAI --> RAG[RAG / Enterprise Search]
    GenAI --> Copilot[AI Copilots]
    GenAI --> Agents[AI Agents]
```

**Important:** This is a conceptual relationship, not a strict hierarchy
in which every NLP system must use deep learning or every AI system must
contain an LLM.

------------------------------------------------------------------------

# 24. AI + Data Engineering: The Big Picture

A Data Engineer can interact with AI at two different levels.

## Level 1 --- Use AI to improve Data Engineering

``` mermaid
flowchart LR
    A[Data Engineer] --> B[AI Assistant]
    B --> C[SQL]
    B --> D[PySpark]
    B --> E[Debugging]
    B --> F[Testing]
    B --> G[Documentation]

    C --> H[Engineer Validation]
    D --> H
    E --> H
    F --> H
    G --> H
    H --> I[Production]
```

## Level 2 --- Build the data foundation for AI

``` mermaid
flowchart LR
    A[Documents / Data Sources] --> B[Ingestion]
    B --> C[Cleaning]
    C --> D[Chunking / Transformation]
    D --> E[Embeddings]
    E --> F[Vector Store]
    F --> G[RAG / AI Application]
    G --> H[User]
```

This is where traditional Data Engineering skills become important for
AI systems:

-   Data ingestion
-   Transformation
-   Data quality
-   Pipeline orchestration
-   Freshness
-   Incremental processing
-   Storage
-   Governance
-   Reliability

------------------------------------------------------------------------

# 25. Data Engineer Interview Cheat Sheet

## AI

**Q: What is AI?**

AI is the broad field of building systems capable of performing tasks
that normally require human intelligence, such as decision making,
language understanding, image recognition, planning, problem solving,
and content generation.

## ML

**Q: What is Machine Learning?**

ML teaches computers to learn patterns from data rather than relying
entirely on explicitly programmed rules.

## Feature

**Q: What is a feature?**

A feature is an input variable used by a machine-learning model, such as
house size or number of bedrooms.

## Label

**Q: What is a label?**

A label is the known target/output used in supervised learning.

## Model

**Q: What is a model?**

A model is a mathematical function that maps inputs to outputs based on
patterns learned during training.

## Supervised Learning

**Q: What is supervised learning?**

It learns from examples containing inputs and known correct answers.
Regression and classification are two major supervised-learning problem
types.

## Unsupervised Learning

**Q: What is unsupervised learning?**

It finds patterns or structure in data without predefined labels, such
as through clustering or anomaly detection.

## Reinforcement Learning

**Q: What is reinforcement learning?**

An agent learns by taking actions, observing outcomes, and receiving
rewards or penalties, with the goal of maximizing future reward.

## Neural Network

**Q: What is a neural network?**

A neural network is a machine-learning model made of connected neurons
arranged in layers, using weights, biases, and activation functions to
learn patterns.

## Deep Learning

**Q: What is Deep Learning?**

Deep Learning uses neural networks with multiple layers to learn
increasingly complex representations.

## NLP

**Q: What is NLP?**

NLP is the AI field focused on processing, understanding, and generating
human language.

## Generative AI

**Q: What is Generative AI?**

Generative AI creates new content such as text, code, images, audio, or
video based on patterns learned from data.

## LLM

**Q: What is an LLM?**

An LLM is a deep-learning model based on Transformer architecture,
trained on massive text/code datasets to learn language patterns and
predict the next token.

## Token

**Q: What is a token?**

A token is a small unit of text processed by an LLM. It can represent a
complete word, part of a word, punctuation, or other text units.

## Embedding

**Q: What is an embedding?**

An embedding is a numerical vector representation of a token or piece of
information that allows a model to process semantic relationships
mathematically.

## Prompt

**Q: What is a prompt?**

A prompt is the input/instruction provided to an LLM.

## Context

**Q: What is context?**

Context is the information currently available to the model while
generating its response, such as previous conversation, retrieved
documents, user data, or tool outputs.

## Temperature

**Q: What does temperature control?**

Temperature influences how strongly generation prefers high-probability
token choices. Lower values generally produce more conservative and
consistent choices, while higher values allow more variation.

## Context Window

**Q: What is a context window?**

It is the amount of information the model can currently see while
processing and generating a response.

## Transformer

**Q: What happens inside a Transformer block?**

The source emphasizes two major components: masked self-attention, which
helps tokens use relevant earlier context, and a feed-forward network,
which further refines the representation.

------------------------------------------------------------------------

# 26. Most Important Distinctions

### AI vs ML

``` text
AI = Broad field
ML = One approach used to build AI systems
```

### ML vs Deep Learning

``` text
ML = Broad machine-learning techniques
Deep Learning = Neural-network-based ML with multiple layers
```

### NLP vs Deep Learning

``` text
NLP = Language problem domain
Deep Learning = Technique that can solve NLP problems
```

### Traditional ML vs Generative AI

``` text
Traditional ML → commonly predicts
Generative AI   → generates new content
```

### Supervised vs Unsupervised

``` text
Supervised   → labeled answers available
Unsupervised → no predefined answers
```

### Embedding vs Token

``` text
Token      → unit of text
Embedding  → numerical vector representation
```

### Prompt vs Context

``` text
Prompt  → instructions/input
Context → information available to help answer
```

### Closed vs Open-weight model

``` text
Closed / Proprietary
→ provider keeps weights private
→ typically accessed through API

Open-weight
→ weights can typically be downloaded
→ can potentially be run, fine-tuned, and deployed on your infrastructure
```

------------------------------------------------------------------------

# 27. 30-Second Mental Model

When explaining AI fundamentals in an interview:

``` text
AI
↓
Machine Learning
↓
Neural Networks
↓
Deep Learning
↓
Transformers
↓
LLMs
↓
Generative AI Applications
↓
RAG / AI Copilots / AI Systems
```

Then connect it back to Data Engineering:

``` text
Reliable Data
↓
Ingestion
↓
Transformation
↓
Quality + Governance
↓
Embeddings / Vector Storage
↓
RAG / AI Application
↓
Useful AI Response
```

> **Final takeaway:** For a Data Engineer, the goal is not to become an
> ML researcher from these fundamentals. The important foundation is
> understanding how AI/ML/LLMs work at a conceptual level and, most
> importantly, how reliable data pipelines enable production AI systems.
