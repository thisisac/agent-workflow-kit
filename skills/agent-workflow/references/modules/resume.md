# Resume across sessions

Input: explicit task pointer, latest user scope, current phase, native execution
evidence and recent decisions. Output: the one unfinished module or a named wait.
Never restart the whole workflow just because context was cleared.

Use persistent working memory as in
[Planning with Files](https://github.com/OthmanAdi/planning-with-files): keep plan,
findings and progress discoverable after compaction. They are views of the same
task, not three independent controllers. With the reference runtime SQLite is the
authority; with an existing project use its real state instead.

Load the compact current view first. Fetch historical artifacts only when they
matter to the next decision. Validate that source/attempt identity did not change
during the read. A later pause or planning-only instruction wins over old ready
flags. An uncertain launch requires reconciliation before any dependent action.

The runtime routes reflection in the same transaction, without a RESUME
callback. Continue reuses research and goes to PLAN; pivot goes to RESEARCH;
wait, complete and stop require their respective conditions. Old RESUME states
are handled by the engine without invoking a host callback. The host invokes
the bounded graph for another wake; installing this skill configures no schedule.
Quiet healthy waits are not material progress.
