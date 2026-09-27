## 3.5.2 Application Log

The Application Log is a record for operational and failure analysis of Runtime, Job, Adapter, Error, and similar activity. It is an artifact separate from Canonical State, Fact, Event, and Audit Record. The design references for this artifact boundary are §2.6, §4, and §28. It is stored under `logs/application/YYYY-MM-DD/`. The component that produces it and the Writer implementation are not yet determined.

The Application Log must not replace Canonical State, Fact, Event, or Audit Record. Deleting the Application Log must not cause the loss of canonical design information, including investment decisions, state, or history. Accordingly, its storage priority is lower than that of Canonical State, Commit, and Audit, and it has a finite retention limit. The specific retention period remains unresolved.

### Rotation and date-based management

The Application Log rotates daily at the `Asia/Tokyo` date boundary. This rotation must make the log manageable in date-based units.

### Information that must not be recorded

The Application Log must not record any of the following:

- a Secret;
- a Credential;
- a Token;
- an API key;
- an Authorization header; or
- an unredacted debug dump.

The range of information, beyond these known prohibited items, that must either be prohibited or masked remains unresolved.

### Write-failure isolation and storage safety

A failure that affects only an Application Log write must not cause a Canonical Commit or canonical investment processing to fail. Such an isolated write failure must be made observable to the extent possible.

This isolation does not override canonical safety. If the same storage failure compromises canonical safety, Storage Fail Closed applies.

### Environment separation

Application Logs must follow the Runtime Identity separation among TEST / PAPER / LIVE. They must also follow the physical separation between Development and Runtime. Logs belonging to these separated environments or domains must not be mixed with one another.

The concrete partition or path scheme that separates TEST / PAPER / LIVE and separates Development / Runtime remains unresolved.

### Unresolved implementation choices

The following matters remain unresolved and must not be treated as fixed implementation requirements:

- the producing component, the Writer responsibilities, and the write path;
- the specific retention period and the method used to perform cleanup or deletion;
- the scope of the Log durability guarantee immediately before a crash;
- the minimum identifying information for each of Runtime, Job, Adapter, and Error;
- the concrete partition or path scheme for environment and domain separation;
- the information, in addition to the known prohibited items, that must be prohibited or masked; and
- the filename, file format, schema, and logging library.
