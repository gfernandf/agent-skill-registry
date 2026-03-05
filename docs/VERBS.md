# Verb list (v0.1)

Verbs are controlled to avoid duplicate capabilities.

## IO verbs

read  
Load content from a source into structured output.

write  
Persist content to a destination.

fetch  
Retrieve content over the network (HTTP or similar).

## Transformation verbs

parse  
Convert raw content into structured data.

extract  
Pull specific fields or entities from content.

transform  
Change representation without changing meaning.

chunk  
Split content into smaller units.

render  
Produce formatted output from templates or structures.

## Reasoning and NLP verbs

summarize  
Produce a shorter representation preserving key points.

classify  
Assign labels or categories.

compare  
Compute differences or similarity.

validate  
Check compliance against rules or schemas.

## Rules

Prefer existing verbs.

Avoid introducing synonyms such as "get" instead of "fetch".

If a new verb is required, it must be proposed through a pull request and added to this document.