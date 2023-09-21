import time
from django.http import HttpResponse
from django.template import loader
from django import forms
from django.http import HttpResponseRedirect

from work.models import WorkItem

from work.tasks import submit_task, check_status


def index(request):
    work_items = WorkItem.objects.all().order_by('-id')
    for w in work_items:
        # assume tasks in memory (finished) stay finished
        # (checking on status of all tasks every time would be too slow)
        if w.status not in ["memory", "does-not-exist"]:
            w.status = check_status(w.task_id)

    WorkItem.objects.bulk_update(work_items, ["status"])
    # latest_question_list = Question.objects.order_by("-pub_date")[:5]
    template = loader.get_template("work/index.html")
    context = {
        "work_items": work_items
    }
    return HttpResponse(template.render(context, request))


class InputsForm(forms.Form):
    sleep_seconds = forms.IntegerField()
    n_copies = forms.IntegerField()

def new_work(request):
    # if this is a POST request we need to process the form data
    if request.method == "POST":
        form = InputsForm(request.POST)

        assert form.is_valid()

        sleep_seconds = form.cleaned_data["sleep_seconds"]

        # let the user submit many copies of each task,
        # just to make it easier to demonstrate scaling
        n_copies = form.cleaned_data["n_copies"]

        for _ in range(n_copies):
            task_id = submit_task(time.sleep, sleep_seconds)
            work_item = WorkItem(sleep_seconds=sleep_seconds, task_id=task_id)
            work_item.save()

        return HttpResponseRedirect("/")
