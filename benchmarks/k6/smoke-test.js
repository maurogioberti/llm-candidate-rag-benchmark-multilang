import http from 'k6/http';
import { check, sleep } from 'k6';

/**
 * Smoke test configuration for basic functionality verification
 * Single user test to validate core RAG pipeline functionality
 */
export const options = {
  vus: 1,
  duration: '30s',
  thresholds: {
    http_req_duration: ['p(95)<300000'], // 5min for LLM processing
    http_req_failed: ['rate<0.1'], // 10% tolerance
  },
  http_req_timeout: '6m',
};

const testQuestions = [
  "Who is the best candidate for .NET backend development?",
  "What candidates have React experience?",
  "What senior profiles are available?",
  "Are there candidates with QA testing experience?",
  "Who has Java backend experience?"
];

const baseUrl = __ENV.BASE_URL || 'http://localhost:5000';

export default function () {
  const question = testQuestions[Math.floor(Math.random() * testQuestions.length)];
  
  const payload = JSON.stringify({ question });
  const params = { headers: { 'Content-Type': 'application/json' } };

  const response = http.post(`${baseUrl}/chat`, payload, params);

  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 5 minutes': (r) => r.timings.duration < 300000,
    'response has answer': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.answer && body.answer.length > 0;
      } catch (e) {
        return false;
      }
    },
    'response has sources': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.sources && Array.isArray(body.sources);
      } catch (e) {
        return false;
      }
    }
  });

  if (response.status !== 200) {
    console.log(`Error: ${response.status} - ${response.body}`);
  }

  sleep(1);
}

export function handleSummary(data) {
  return {
    'smoke-test-results.json': JSON.stringify(data, null, 2),
  };
}
