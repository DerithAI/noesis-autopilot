/**
 * Zod Validation Schemas for EVO-HUB Frontend
 * Phase 2.4: Input validation for frontend forms
 */
import { z } from 'zod';

// ─── Enums ─────────────────────────────────────────────────────────────────

export const VentureStatus = z.enum(['deployed', 'live', 'failed', 'generating']);
export type VentureStatus = z.infer<typeof VentureStatus>;

export const PipelineStage = z.enum(['Observe', 'Research', 'Architect', 'Implement', 'Test', 'Deploy']);
export type PipelineStage = z.infer<typeof PipelineStage>;

export const CognitiveMode = z.enum(['chat', 'analyze', 'generate', 'verify']);
export type CognitiveMode = z.infer<typeof CognitiveMode>;

export const HowlFrequency = z.enum(['low', 'medium', 'high', 'AUUUU']);
export type HowlFrequency = z.infer<typeof HowlFrequency>;

export const ModelComplexity = z.enum(['low', 'medium', 'high']);
export type ModelComplexity = z.infer<typeof ModelComplexity>;

const ModelName = z.enum([
  'qwen2.5:3b',
  'qwen2.5:7b',
  'deepseek-r1',
  'qwen3:8b',
  'llama3.2:3b',
  'hermes3:7b',
  'dolphin3:7b'
]);

const StackOption = z.enum(['auto', 'fastapi', 'fastapi+react', 'nextjs', 'django', 'express']);

const CognitiveModeEnum = z.enum(['chat', 'analyze', 'generate', 'verify']);

const HowlFrequencyEnum = z.enum(['low', 'medium', 'high', 'AUUUU']);

const ModelComplexityEnum = z.enum(['low', 'medium', 'high']);

// ─── Venture Schemas ────────────────────────────────────────────────────────

export const VentureSeedSchema = z.object({
  seed: z.string()
    .min(3, 'Seed must be at least 3 characters')
    .max(200, 'Seed must be at most 200 characters')
    .refine((val) => !/[;&|`$]/.test(val), 'Seed contains invalid characters'),
  model: ModelName.optional(),
  stack: StackOption.default('auto'),
  complexity: ModelComplexityEnum.default('medium'),
});

export type VentureSeedInput = z.infer<typeof VentureSeedSchema>;

export const VentureResponseSchema = z.object({
  name: z.string(),
  seed: z.string(),
  stack: z.string(),
  files: z.number().int().nonnegative(),
  status: VentureStatus,
  created_at: z.string().datetime().optional(),
});

export type VentureResponse = z.infer<typeof VentureResponseSchema>;

// ─── System Status ──────────────────────────────────────────────────────────

export const SystemStatusResponseSchema = z.object({
  evo_hub: z.boolean(),
  lumen: z.boolean(),
  ollama: z.boolean(),
  ventures: z.number().int().nonnegative(),
});

export type SystemStatusResponse = z.infer<typeof SystemStatusResponseSchema>;

export const PipelineResponseSchema = z.object({
  steps: z.array(z.string()),
  current: z.string(),
  active_venture: z.string(),
});

export type PipelineResponse = z.infer<typeof PipelineResponseSchema>;

// ─── Action Requests ────────────────────────────────────────────────────────

export const GenerateRequestSchema = z.object({
  seed: z.string().min(3).max(200),
  model: ModelName.default('qwen2.5:7b'),
  stack: StackOption.default('auto'),
});

export type GenerateRequest = z.infer<typeof GenerateRequestSchema>;

export const CognitiveRequestSchema = z.object({
  input: z.string().min(1).max(5000),
  mode: CognitiveModeEnum.default('chat'),
});

export type CognitiveRequest = z.infer<typeof CognitiveRequestSchema>;

export const HowlRequestSchema = z.object({
  message: z.string().min(1).max(500),
  frequency: HowlFrequencyEnum.default('medium'),
});

export type HowlRequest = z.infer<typeof HowlRequestSchema>;

export const CognitiveLoopRequestSchema = z.object({
  input: z.string().min(1).max(5000),
  use_council: z.boolean().default(true),
});

export type CognitiveLoopRequest = z.infer<typeof CognitiveLoopRequestSchema>;

// ─── ITDD ────────────────────────────────────────────────────────────────────

export const ITDDEntrySchema = z.object({
  venture: z.string(),
  compliant: z.boolean(),
  tests: z.number().int().nonnegative(),
  passed: z.number().int().nonnegative(),
  failed: z.number().int().nonnegative(),
  note: z.string().optional(),
});

export type ITDDEntry = z.infer<typeof ITDDEntrySchema>;

export const ITDDStatusResponseSchema = z.object({
  total_ventures: z.number().int().nonnegative(),
  compliant: z.number().int().nonnegative(),
  with_tests: z.number().int().nonnegative(),
  coverage_ratio: z.number().min(0).max(1),
  compliance_ratio: z.number().min(0).max(1),
  scoreboard: z.array(ITDDEntrySchema),
});

export type ITDDStatusResponse = z.infer<typeof ITDDStatusResponseSchema>;

// ─── Council ─────────────────────────────────────────────────────────────────

export const CouncilVoiceResponseSchema = z.object({
  role: z.string(),
  recommendation: z.string(),
  confidence: z.number().int().min(0).max(100),
  reasoning: z.string(),
});

export type CouncilVoiceResponse = z.infer<typeof CouncilVoiceResponseSchema>;

export const CouncilDeliberateRequestSchema = z.object({
  decision: z.string().min(3).max(1000),
  context: z.string().max(2000).default(''),
  require_unanimous: z.boolean().default(false),
});

export type CouncilDeliberateRequest = z.infer<typeof CouncilDeliberateRequestSchema>;

export const CouncilDeliberateResponseSchema = z.object({
  recommendation: z.string(),
  confidence: z.number().int().min(0).max(100),
  unanimous: z.boolean(),
  voices: z.array(CouncilVoiceResponseSchema),
  context: z.string(),
});

export type CouncilDeliberateResponse = z.infer<typeof CouncilDeliberateResponseSchema>;

export const CouncilVoicesResponseSchema = z.object({
  voices: z.array(z.object({
    role: z.string(),
    description: z.string(),
    weight: z.number(),
    concerns: z.array(z.string()),
  })),
});

export type CouncilVoicesResponse = z.infer<typeof CouncilVoicesResponseSchema>;

// ─── Memory ──────────────────────────────────────────────────────────────────

export const MemorySearchRequestSchema = z.object({
  query: z.string().min(1).max(500),
  limit: z.number().int().min(1).max(50).default(5),
});

export type MemorySearchRequest = z.infer<typeof MemorySearchRequestSchema>;

export const MemorySearchResultSchema = z.object({
  source: z.string(),
  id: z.string().optional(),
  content: z.string(),
  timestamp: z.string().optional(),
  score: z.number().optional(),
});

export type MemorySearchResult = z.infer<typeof MemorySearchResultSchema>;

export const MemorySearchResponseSchema = z.object({
  query: z.string(),
  count: z.number().int().nonnegative(),
  sources: z.array(z.string()),
  results: z.array(MemorySearchResultSchema),
});

export type MemorySearchResponse = z.infer<typeof MemorySearchResponseSchema>;

// ─── OMEGA ───────────────────────────────────────────────────────────────────

export const OmegaHealthResponseSchema = z.object({
  available: z.boolean(),
  gateway: z.string(),
  status: z.string(),
  note: z.string().optional(),
});

export type OmegaHealthResponse = z.infer<typeof OmegaHealthResponseSchema>;

export const OmegaNodeSchema = z.object({
  name: z.string(),
  port: z.number().int(),
  capabilities: z.array(z.string()),
});

export type OmegaNode = z.infer<typeof OmegaNodeSchema>;

export const OmegaNodesResponseSchema = z.object({
  available: z.boolean(),
  nodes: z.array(OmegaNodeSchema).default([]),
  error: z.string().optional(),
});

export type OmegaNodesResponse = z.infer<typeof OmegaNodesResponseSchema>;

export const DispatchPayloadSchema = z.object({
  target_node: z.string().min(1),
  task_data: z.record(z.unknown()),
});

export type DispatchPayload = z.infer<typeof DispatchPayloadSchema>;

export const DispatchResponseSchema = z.object({
  success: z.boolean(),
  error: z.string().optional(),
});

export type DispatchResponse = z.infer<typeof DispatchResponseSchema>;

// ─── Error Response ──────────────────────────────────────────────────────────

export const ErrorResponseSchema = z.object({
  detail: z.string(),
  code: z.string().optional(),
  field: z.string().optional(),
});

export type ErrorResponse = z.infer<typeof ErrorResponseSchema>;

// ─── Validation Helpers ──────────────────────────────────────────────────────

/**
 * Validate data against a schema, return { success: boolean, data?: T, errors?: string[] }
 */
export function validate<T>(schema: z.ZodSchema<T>, data: unknown): {
  success: boolean;
  data?: T;
  errors?: string[];
} {
  const result = schema.safeParse(data);
  if (result.success) {
    return { success: true, data: result.data };
  }
  return {
    success: false,
    errors: result.error.errors.map(e => `${e.path.join('.')}: ${e.message}`),
  };
}

/**
 * Form validation hook for React
 */
export function useValidation<T>(schema: z.ZodSchema<T>) {
  return (data: unknown) => validate(schema, data);
}

// ─── Export All ──────────────────────────────────────────────────────────────

export const schemas = {
  VentureSeed: VentureSeedSchema,
  VentureResponse: VentureResponseSchema,
  SystemStatus: SystemStatusResponseSchema,
  Pipeline: PipelineResponseSchema,
  GenerateRequest: GenerateRequestSchema,
  CognitiveRequest: CognitiveRequestSchema,
  HowlRequest: HowlRequestSchema,
  CognitiveLoopRequest: CognitiveLoopRequestSchema,
  ITDDEntry: ITDDEntrySchema,
  ITDDStatus: ITDDStatusResponseSchema,
  CouncilVoice: CouncilVoiceResponseSchema,
  CouncilDeliberateRequest: CouncilDeliberateRequestSchema,
  CouncilDeliberateResponse: CouncilDeliberateResponseSchema,
  CouncilVoices: CouncilVoicesResponseSchema,
  MemorySearchRequest: MemorySearchRequestSchema,
  MemorySearchResult: MemorySearchResultSchema,
  MemorySearchResponse: MemorySearchResponseSchema,
  OmegaHealth: OmegaHealthResponseSchema,
  OmegaNode: OmegaNodeSchema,
  OmegaNodes: OmegaNodesResponseSchema,
  DispatchPayload: DispatchPayloadSchema,
  DispatchResponse: DispatchResponseSchema,
  Error: ErrorResponseSchema,
};

export default schemas;