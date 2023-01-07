from django.contrib import messages
from django.http import HttpResponse, Http404
from qa.models import Question, Answer
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from .forms import AskForm, AnswerForm


def test(request, *args, **kwargs):
    return HttpResponse('OK')


def ask(request):
    if request.method == 'POST':
        form = AskForm(request.POST)
        if form.is_valid():
            question = form.save()
            url = question.get_url()
            return redirect(url)
    else:
        form = AskForm()
    return render(request, 'qa/ask.html', {'form': form})


def page_not_found_view(request, exception):
    return render(request, 'qa/404.html', status=200)


def popular(request, *args, **kwargs):
    qts = Question.objects.popular()
    page_obj = paginate(request, qts)
    return render(request, 'qa/new.html', {
        'questions': page_obj.object_list,
        'page_obj': page_obj,
        'title': 'List of popular questions',
    })


def question_info(request, q_id):
    try:
        q = int(q_id)
    except TypeError:
        raise Http404()
    try:
        question = Question.objects.get(pk=q)
    except IndexError:
        raise Http404()

    if request.method == 'POST':
#        form = AnswerForm(request.POST, question=question)
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save()
            messages.success(request, 'Answer added successfully.')
            return redirect(request.path)
    else:
        form = AnswerForm()
#        form = AnswerForm(question=question)
    answers = Answer.objects.filter(question=question).order_by('-added_at')
    return render(request, 'qa/question.html', {
        'question': question,
        'answers': answers,
        'form': form,
    })


def new(request, *args, **kwargs):
    qts = Question.objects.new()
    page_obj = paginate(request, qts)
    return render(request, 'qa/new.html', {
        'questions': page_obj.object_list,
        'page_obj': page_obj,
        'title': 'List of recent questions',
    })


def paginate(request, qset):
    try:
        limit = int(request.GET.get('limit', 10))
    except ValueError:
        limit = 10
    if limit > 100:
        limit = 100

    try:
        page_number = int(request.GET.get('page', 1))
    except ValueError:
        raise handler404
    paginator = Paginator(qset, limit)
    try:
        page_obj = paginator.page(page_number)
    except:
        page_obj = paginator.page(paginator.num_pages)

    return page_obj


def scrap(request, *args, **kwargs):
    import requests
    from bs4 import BeautifulSoup
    import re

    # res = requests.get('https://parade.com/1025605/marynliles/trick-questions/')

    with open('/home/mit/Documents/125 Trick Questions (with Answers) That Are Confusing - Parade Entertainment, Recipes, Health, Life, Holidays.html') as file:
        content = file.read()
    html = BeautifulSoup(content, 'html.parser')
    qts = html.select('p')
    questions = []
    answers = []
    for q in qts:
        try:
            res = re.match(r'^\d+\.', q.string)
            if res:
                text = re.sub(r'^\d+\.\s', '', q.string)
                if len(text) > 50:
                    title = text[:50] + '...'
                else:
                    title = text
                quest = Question(title=title, text=text, author=request.user)
                # quest.save()
                questions.append(quest)
                ans = Answer(text=qts[qts.index(q)+1].string, question=quest, author=request.user)
                #ans.save()
                answers.append(ans)
        except TypeError:
            continue

    return render(request, 'qa/new1.html', context={'questions': zip(questions, answers)})


