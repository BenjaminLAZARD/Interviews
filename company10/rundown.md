# Building a family tree from a textual book

I have at hand a .txt file with the content of a book. This is zola's "La Fortune des Rougon".

I want to build a series of tools that will eventually build a family tree of les Rougons.
I can use LLMs (I have an OpenAI api key in .env).

Most code is in Python

Here are some debuggable intermediary steps to reach that result

1. Preprocessing: Block the Text

- Split into 30,000 chars chunks, with 2,000 chars from the previous block at the beginning of each block.
- Save blocks under ./0/text.txt, ./1/text.txt, etc.
- The metadata used to split could be stored as well

2. Retrieve names for each character

- List all character names, with known nicknames. "name" -> [nickname1, nickname2, etc.]"
- Always include surnames if known.
- If they are Rougon family members, prefix with *. (they may be affilitated with Rougon but not directly bear the name like in weddings)

Save in ./i/names.txt.

3. Consolidate Characters

- Merge all names list
- Proper conflict management rules (duplicated names or nicknames, asterisks found unilaterally, etc.)

4. Tag Character Mentions in Blocks

- Using the consolidated list of names, ask LLM to bracket the names in each block.
- For example: "Pierre Rougon" ➔ [Pierre Rougon].
- Create new file ./i/bracketed.txt for each block.

5. Extract Family Relationships per Block

- For each bracketed.txt block, ask LLM to detect any clear family link :
- A -> B [parent], etc.
- One way only whenever possible (no redundant child->parent).
- Creating unknown whenever possible
- Save family relations for each block in ./i/relations.txt.

6. Merge All Relations into One Graph

- Gather all relations.txt into a single master list.
- Deal with conflicts as in the list of names.

7. Rewrite All Relations as [parent] and [married]

8. Build the GraphViz .dot File

- Convert final_relations.txt into a DOT file for Graphviz Vizualisation.
- One node per person or couple
