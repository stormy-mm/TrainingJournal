from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404

from .models import Topic, Entry
from .forms import TopicForm
from .forms import EntryForm


def _check_topic_owner(owner, user):
    """Проверяет, принадлежит ли тема пользователю"""
    if owner != user:
        raise Http404


def index(request):
    """Главная страница приложения "Журнал обучения"."""
    return render(request, "learning_logs/index.html")


@login_required
def topics(request):
    """Выводит темы"""
    topics_ = Topic.objects.filter(owner=request.user).order_by("date_added")
    context = {'topics': topics_}
    return render(request, "learning_logs/topics.html", context)


@login_required
def topic(request, topic_id):
    """Выводит одну тему и все её записи"""
    topic_ = Topic.objects.get(id=topic_id)
    # Проверка того, что тема принадлежит текущему пользователю
    _check_topic_owner(topic_.owner, request.user)

    entries = topic_.entry_set.order_by("-date_added")
    context = {"topic": topic_, "entries": entries}
    return render(request, "learning_logs/topic.html", context)


@login_required
def new_topic(request):
    """Добавляет новую тему"""
    if request.method != "POST":
        # данные не отправлялись; создаётся пустая форма
        form = TopicForm()
    else:
        # отправлены данные POST; обработать данные
        form = TopicForm(data=request.POST)
        if form.is_valid():
            new_topic = form.save(commit=False)
            new_topic.owner = request.user
            new_topic.save()
            return redirect("learning_logs:topics")

    #  вывести пустую или недействительную форму
    context = {"form": form}
    return render(request, "learning_logs/new_topic.html", context)


@login_required
def new_entry(request, topic_id):
    """Добавляет новую запись по конкретной теме"""
    topic_ = Topic.objects.get(id=topic_id)
    _check_topic_owner(topic_.owner, request.user)

    if request.method != "POST":
        form = EntryForm()
    else:
        form = EntryForm(data=request.POST)
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.topic = topic_
            new_entry.save()

            return redirect("learning_logs:topic", topic_id=topic_id)

    context = {"topic": topic_, "form": form}
    return render(request, "learning_logs/new_entry.html", context)


@login_required
def edit_entry(request, entry_id):
    """Редактирует существующую запись"""
    entry = Entry.objects.get(id=entry_id)
    topic = entry.topic
    _check_topic_owner(topic.owner, request.user)

    if request.method != "POST":
        form = EntryForm(instance=entry)
    else:
        form = EntryForm(data=request.POST, instance=entry)
        if form.is_valid():
            form.save()
            return redirect("learning_logs:topic", topic_id=topic.id)

    context = {"entry": entry, "topic": topic, "form": form}
    return render(request, "learning_logs/edit_entry.html", context)

