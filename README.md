Django Coiled Dask Example
==========================

This is an example project showing how one might use Coiled and Dask to offload expensive tasks from a Django project.

To set up your environment:

```
conda create -n django-dask python=3.11 django coiled -c conda-forge
conda activate django-dask
python manage.py migrate
```

To use this you need a Coiled cluster running. I'd recommend that something outside the web server is responsible for starting the cluster (and making a new one if that ever becomes necessary):

```python
import coiled

cluster = coiled.Cluster(
    name="prod",
    scheduler_vm_types="m6g.medium",  # small 24x7 instance
    worker_vm_types="m6g.2xlarge",    # larger compute instances
    spot_policy="spot_with_fallback",
    n_workers=1,
    idle_timeout="52 weeks",          # Don't shut down
    shutdown_on_close=False,
)
```

Then to start the app:

```
python manage.py runserver
```

## Some additional notes

* We've cached the Dask client instead of making a new client each time we need one.  Response times should be in the 50-100ms range.  The cached client is also responsible for driving the autoscaling behavior of the Dask cluster.
* In this example, we're checking on task status in the path of a web request. It might be better to do that somewhere else and store the state, so individual web requests don't need this.
* As written, the futures stay on the Dask cluster in memory forever. If the results are tiny, that might not be a big deal, but it's probably necessary to clear them out eventually.  To clear things out we'd want to empty the queue holding onto them periodically.  There are many ways to achieve this.
* This assumes that the Dask cluster survives forever.  This might not be true.
  There are some other architectures that might makes sense:

    *   Create a fresh Coiled cluster on every request, perhaps with some
        keepalive time.  To do this well we'll need to buffer the django app
        from the minute-long startup time.  Maybe a tiny Celery/RabbitMQ
        system could help here.
    *   Leverage a workflow manager like Prefect/Dagster on top of Dask/Coiled
    *   Intentionally cycle the scheduler

    These are all doable, but make things a bit more complicated.  We're
    starting simple here, and we expect this to work well for most
    applications.

<img width="722" alt="Screen Shot 2023-09-21 at 4 29 51 PM" src="https://github.com/coiled/django-dask/assets/1222726/b47af46d-4c08-46ba-a790-606a2dd8b9c3">
