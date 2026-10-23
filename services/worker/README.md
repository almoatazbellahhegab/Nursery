# Worker boundary

TW-011 directory scaffold only. Workers will consume durable outbox messages, acknowledge after durable completion, deduplicate operations and record terminal failures. No queue consumer is implemented. TW-032 and approved infrastructure are prerequisites.
