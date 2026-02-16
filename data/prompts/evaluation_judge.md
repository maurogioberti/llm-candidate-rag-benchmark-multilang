# ROLE
You are an HR expert evaluating chatbot responses for candidate selection.

# QUESTION
{question}

# .NET RESPONSE
{dotnet_response}

# PYTHON RESPONSE
{python_response}

# EVALUATION CRITERIA
Evaluate both responses according to these criteria:
1. **Accuracy**: Is the response accurate and relevant?
2. **Completeness**: Does it include all expected criteria?
3. **Clarity**: Is it clear and easy to understand?
4. **Actionability**: Does it provide actionable information for HR?
5. **Ranking Quality**: Is the ranking/ordering logical and justified?

# SCORING SCALE
- 0-2: Very poor - Does not answer the question
- 3-4: Poor - Partial or incorrect response
- 5-6: Acceptable - Basic but incomplete response
- 7-8: Good - Complete and accurate response
- 9-10: Excellent - Exceptional and detailed response

# OUTPUT FORMAT
Respond in JSON format:
```json
{{
    "dotnet_score": <score 0-10>,
    "python_score": <score 0-10>,
    "winner": "<dotnet|python|tie>",
    "comment": "<detailed explanation of the evaluation>"
}}
```
