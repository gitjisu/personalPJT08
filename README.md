1. 비동기 코드 복습 필요 
2. 이번에는 추천 알고리즘을 tmdb걸로 가져다가 썼는데 한계점이 많음 -> 보완필요 / 장르를 사용자의 입력을 받거나, 사용자 관련 알고리즘으로 추천해준다면 좋을 것 같다. 
3. url 집어넣을때  ``img src="{{ poster|add:movie.poster_path }}"`` 교수님의 도움으로 해결 했다! ``|add`` 기억 해 두자!

```
{% extends 'base.html' %}

{% block content %}
  <h1>Community</h1>
  <hr>
  {% for review in reviews %}
  <p>
    <b>작성자 : <a href="{% url 'accounts:profile' review.user.username %}">{{ review.user }}</a></b>
  </p>
  <p>글 번호 : {{ review.pk }}</p>
  <p>글 제목 : {{ review.title }}</p>
  <p>글 내용 : {{ review.content }}</p>
  <div>
    <form class="like-form" data-id="{{ review.pk }}">
      {% csrf_token %}
      {% if request.user in review.like_users.all %}
        <button id="like-{{ review.pk }}">좋아요 취소</button>
      {% else %}
        <button id="like-{{ review.pk }}">좋아요</button>
      {% endif %}
    </form>
  </div>
  <p>
    <span id="like-count-{{ review.pk }}">{{ review.like_users.all|length }}</span>
    명이 이 글을 좋아합니다.</p>
  <a href="{% url 'community:detail' review.pk %}">[DETAIL]</a>
  <hr>
{% endfor %}
<script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
  <script>
    // 1. form 태그(좋아요 버튼) 전부다 가져오기
    const forms = document.querySelectorAll('.like-form')
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value

    forms.forEach(function (form) {
      
      form.addEventListener('submit', function (event) {
        event.preventDefault()
        // console.log(event)
        const reviewId = event.target.dataset.id
        // console.log(csrftoken)
        axios.post(`http://127.0.0.1:8000/community/${reviewId}/like/`, {}, {
          headers: {'X-CSRFToken': csrftoken},
        })
        .then(function (response) {
          console.log(response.data)

          //const count = response.data.count
          //const liked = response.data.liked
          
          const { count, liked } = response.data
          // console.log(count, liked)

          const likeButton = document.querySelector(`#like-${reviewId}`)
          if (liked) {
            likeButton.innerText = '좋아요 취소'
          } else {
            likeButton.innerText = '좋아요'
          }
          // likeButton.innerText = liked ? '좋아요 취소' : '좋아요'

          const likeCount = document.querySelector(`#like-count-${reviewId}`)
          likeCount.innerText = count

        })
        .catch(err => {
          console.log(err.response.status)
          if (err.response.status === 401) {
            window.location.href = '/accounts/login/'
          }
        })
      })
    })
  </script>
{% endblock %}

```

```

@require_POST
def like(request, review_pk):
    if request.user.is_authenticated:
        review = get_object_or_404(Review, pk=review_pk)

        if review.like_users.filter(pk=request.user.pk).exists():
        # if request.user in review.like_users.all():
            # 좋아요 취소
            review.like_users.remove(request.user)
            liked = False
        else:
            # 좋아요 누름
            review.like_users.add(request.user)
            liked = True
        
        like_status = {
            'liked': liked,
            'count': review.like_users.count(),
        }
        return JsonResponse(like_status)
    return HttpResponse(status=401)
```

```
{% extends 'base.html' %}

{% block content %}
  <h1>{{ person.username }}의 프로필 페이지</h1>
  {% with followings=person.followings.all followers=person.followers.all %}
  <div>
    <div id="follow-count">
      팔로잉 : {{ followings|length }} / 팔로워 : {{ followers|length }}
    </div>
    {% if request.user != person %}
      <div>
        <form id="follow-form" data-user-id="{{ person.pk }}">
          {% csrf_token %}
          {% if request.user in followers %}
            <button>언팔로우</button>
          {% else %}
            <button>팔로우</button>
          {% endif %}
        </form>
      </div>
    {% endif %}
  </div>
{% endwith %}


<hr>

<h2>{{ person.username }}'s 게시글</h2>
{% for movie in person.movie_set.all %}
  <div>{{ movie.title }}</div>
{% endfor %}

<hr>

<h2>{{ person.username }}'s 댓글</h2>
{% for comment in person.comment_set.all %}
  <div>{{ comment.content }}</div>
{% endfor %}

<hr>

<h2>{{ person.username }}'s likes</h2>
{% for movie in person.like_movies.all %}
  <div>{{ movie.title }}</div>
{% endfor %}

<hr>

<a href="{% url 'movies:index' %}">[back]</a>

<script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
<script>

  const form = document.querySelector('#follow-form')
  const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value

  form.addEventListener('submit', function (event) {
    event.preventDefault()
    const userId = event.target.dataset.userId

    axios({
      method: 'post',
      url: `/accounts/${userId}/follow/`,
      headers: {'X-CSRFToken': csrftoken},
    })
    .then(response => {
      console.log(response)
      const followersCount = response.data.followers_count
      const followingsCount = response.data.followings_count
      const followed = response.data.followed

      const followCount = document.querySelector('#follow-count')
      followCount.innerText = `팔로잉: ${followingsCount} / 팔로워: ${followersCount}`

      const followBtn = document.querySelector('#follow-form > button')
      if (followed) {
        followBtn.innerText = '언팔로우'
      } else {
        followBtn.innerText = '팔로우'
      }

    })

  })

</script>

{% endblock %}

```

```

@require_POST
def follow(request, user_pk):
    if request.user.is_authenticated:
        # 팔로우 받는 사람
        you = get_object_or_404(get_user_model(), pk=user_pk)
        me = request.user

        # 나 자신은 팔로우 할 수 없다.
        if you != me:
            if you.followers.filter(pk=me.pk).exists():
            # if request.user in person.followers.all():
                # 팔로우 끊음
                you.followers.remove(me)
                followed = False
            else:
                # 팔로우 신청
                you.followers.add(me)
                followed = True
            follow_status = {
                'followers_count': you.followers.count(),
                'followings_count': you.followings.count(),
                'followed': followed,
            }
            return JsonResponse(follow_status)
        return redirect('accounts:profile', you.username)
    return redirect('accounts:login')

```

