aurora-rpm-spec
===============

RPM spec for Apache Aurora.

Assumes the use of tito and mock, for now. Some customization will likely be
required for your environment. Check the instructions in the spec file.

This will generate three RPMs:

- aurora-scheduler: deploy this on machines that will host the sheduler.
- aurora-thermos: deploy this on mesos slaves.
- aurora-client: deploy this on machines on which you will interact with aurora
    from the command line.

Init and config scripts are not included, but I'd be happy to add them if there
is interest.
