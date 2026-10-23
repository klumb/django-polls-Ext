from django.db.models import F
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.views.generic.edit import CreateView
from django.utils import timezone
from .models import Choice, Question, Comment


class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """
        Return the last six published questions (not including those set to be
        published in the future).
        """
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")[:6]
    # ...
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        visited = self.request.COOKIES.get("visited_polls")
        if visited:
            context["message"] = "Welcome back to the Polls application."
        else:
            context["message"] = "Welcome to the Polls application."
        # ...
        count = self.request.session.get("visit_count", 0)
        count += 1
        self.request.session["visit_count"] = count
        context["visit_count"] = count

        # ...
        last_poll_id = self.request.session.get("last_poll")
        last_poll = None

        if last_poll_id:
            try:
                last_poll = Question.objects.get(pk=last_poll_id)
            except Question.DoesNotExist:
                pass

        context["last_poll"] = last_poll

        return context
    # ...
    def render_to_response(self, context, **response_kwargs):
        response = super().render_to_response(context, **response_kwargs)
        response.set_cookie("visited_polls", "yes", max_age=120)
        return response

class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())

    # ...
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.request.session["last_poll"] = self.object.id
        return context

class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))
#...
class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    fields = ["text"]

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.question_id = self.kwargs["question_id"]

        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "polls:detail",
            kwargs={"pk": self.kwargs["question_id"]}
        )





