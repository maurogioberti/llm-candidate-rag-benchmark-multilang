import http from 'k6/http';
import { check, sleep } from 'k6';

/**
 * Stress test configuration to find system breaking point
 * Aggressive load testing to identify performance bottlenecks
 */
export const options = {
  stages: [
    { duration: '2m', target: 10 },
    { duration: '5m', target: 10 },
    { duration: '2m', target: 50 },
    { duration: '5m', target: 50 },
    { duration: '2m', target: 100 },
    { duration: '5m', target: 100 },
    { duration: '2m', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000'], // 2s for stress testing
    http_req_failed: ['rate<0.1'], // 10% tolerance
  },
};

const testQuestions = [
  "Who is the best candidate for .NET backend development?",
  "What candidates have React experience?",
  "What senior profiles are available?",
  "Are there candidates with QA testing experience?",
  "Who has Java backend experience?",
  "What candidates have API testing experience?",
  "Are there full-stack developers available?",
  "Who has Azure cloud experience?",
  "What candidates speak fluent English?",
  "Are there frontend developers available?",
  "Who has Spring Boot experience?",
  "What candidates have JavaScript experience?",
  "Are there QA manual testers available?",
  "Who has SQL database experience?",
  "What candidates have Git experience?"
];

const baseUrl = __ENV.BASE_URL || 'http://localhost:5000';

export default function () {
  const question = testQuestions[Math.floor(Math.random() * testQuestions.length)];
  
  const payload = JSON.stringify({ question });
  const params = { headers: { 'Content-Type': 'application/json' } };

  const response = http.post(`${baseUrl}/chat`, payload, params);

  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 2s': (r) => r.timings.duration < 2000,
    'response has answer': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.answer && body.answer.length > 0;
      } catch (e) {
        return false;
      }
    }
  });

  if (response.status !== 200) {
    console.log(`Error: ${response.status} - ${response.body}`);
  }

  sleep(0.1);
}

export function handleSummary(data) {
  return {
    'stress-test-results.json': JSON.stringify(data, null, 2),
  };
}
