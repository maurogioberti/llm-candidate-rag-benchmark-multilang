import http from 'k6/http';
import { check, sleep } from 'k6';

/**
 * Load test configuration for RAG workloads
 * Tests system behavior under sustained load with gradual user ramp-up
 */
export const options = {
  stages: [
    { duration: '2m', target: 10 },
    { duration: '5m', target: 10 },
    { duration: '2m', target: 20 },
    { duration: '5m', target: 20 },
    { duration: '2m', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<1800000'], // 30min for LLM processing
    http_req_failed: ['rate<0.3'], // 30% tolerance for RAG workloads
    http_reqs: ['rate>0.05'], // Minimum throughput
  },
  http_req_timeout: '30m',
  noConnectionReuse: false,
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
  "Are there frontend developers available?"
];

const baseUrl = __ENV.BASE_URL || 'http://localhost:5000';

export default function () {
  const question = testQuestions[Math.floor(Math.random() * testQuestions.length)];
  
  const payload = JSON.stringify({ question });
  const params = { headers: { 'Content-Type': 'application/json' } };

  const response = http.post(`${baseUrl}/chat`, payload, params);

  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 30 minutes': (r) => r.timings.duration < 1800000,
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

  sleep(10);
}

export function handleSummary(data) {
  return {
    'load-test-results.json': JSON.stringify(data, null, 2),
  };
}
