// АВТОСЛАЙДИНГ
var photo_slides_interval = null;
function runPhotoSlider() {
	// Создаем интервал
	photo_slides_interval = setInterval(function () {
		var slides = parseInt($(".photo_slider ul.slides").find('li').length);
		var next_slide = parseInt($(".photo_slider ul.slides").attr('alt')) + 1;
		if (next_slide > slides) next_slide = 1;
		showSlide(next_slide);

	}, 3000);
}

// ПОКАЗАТЬ СЛАЙД
function showSlide(pos) {
	$('.photo_slider ul.controls li.set').removeClass('set');
	$(".photo_slider ul.slides").animate({ marginLeft: -((pos * 460) - 460) }, 500,
		function () {
			$(".photo_slider ul.slides").attr('alt', pos);
			$('.photo_slider ul.controls li[alt="' + pos + '"]').addClass('set');
		});
}

//СОБЫТИЯ
$(function () {
	$.datepicker.setDefaults({
		firstDay: 1,
		dateFormat: 'yy-mm-dd',
		dayNames: ['Воскресенье', 'Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота'],
		dayNamesMin: ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'],
		monthNames: ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'],
		duration: 'fast',
		changeYear: true

	});

	// Фотографии
	$('.fancy_image').fancybox();

	// Подготовка салайдера
	var photo_slides_count = parseInt($(".photo_slider ul").find('li').length);
	$(".photo_slider ul.slides").css(
		{
			marginLeft: 0,
			width: photo_slides_count * 460

		}).attr('alt', 1);

	// Управление слайдингом
	if (photo_slides_count > 0) {
		for (var i = 1; i <= photo_slides_count; i++) {
			var set = '';
			if (i == 1) set = ' class="set"';
			$('.photo_slider .controls').append('<li alt="' + i + '"' + set + '></li>');
		}
	}

	// Переход на слайд
	$('.photo_slider .controls li').click(function () {
		if (!$(this).hasClass('set')) {
			clearInterval(photo_slides_interval);
			showSlide(parseInt($(this).attr('alt')));
			setTimeout(function () { runPhotoSlider() }, 10000);
		}
	});

	// Запуск автослайдинга
	runPhotoSlider();

	// Instagram Show More (using .live() for jQuery 1.4.2 compatibility)
	$('#ig-show-more-btn').live('click', function (e) {
		e.preventDefault();
		var $btn = $(this);
		var after = $btn.attr('data-after');
		if (!after) return;

		$btn.attr('disabled', 'disabled').text(igLang === "en" ? "Loading…" : "Загрузка…"); // Loading state

		var lang = 'ru';
		var match = window.location.pathname.match(/\/(ru|en|kz)\//);
		if (match) lang = match[1];

		$.ajax({
			url: '/ajax.php',
			type: 'POST',
            timeout: 12000,
			data: { go: 'load_more_instagram', after: after, lang: lang },
			success: function (resp) {
				try {
					var data = (typeof resp === 'string') ? JSON.parse(resp) : resp;
if(!data || typeof data !== 'object') throw new Error('Invalid feed response');

					if (data.error) {
						console.error('Instagram is temporarily unavailable');
						$("#ig-feedback").text(data.message || (igLang === "en" ? "Instagram is temporarily unavailable. Please use the profile link." : "Instagram временно недоступен. Откройте профиль по ссылке."));
						$btn.removeAttr('disabled').text(igLang === "en" ? "Show more" : "Показать ещё");
						return;
					}

					if (data.html) {
						$('#ig-grid-content').append(data.html);
if(data.posts && data.posts.length){ for(var p=0;p<data.posts.length;p++){var found=false;for(var k=0;k<igPostsData.length;k++)if(igPostsData[k].id===data.posts[p].id)found=true;if(!found)igPostsData.push(data.posts[p]);}igNextCursor=data.next_cursor||null;}
					} else {
					}

					if (data.next_cursor) {
						$btn.attr('data-after', data.next_cursor).removeAttr('disabled').text(igLang === "en" ? "Show more" : "Показать ещё");
					} else {
						$btn.parent().remove();
					}
				} catch (e) {
					console.error('Error parsing response');$("#ig-feedback").text(igLang === "en" ? "Instagram is temporarily unavailable. Please use the profile link." : "Instagram временно недоступен. Откройте профиль по ссылке.");
					$btn.removeAttr('disabled').text(igLang === "en" ? "Show more" : "Показать ещё");
				}
			},
			error: function () {
$("#ig-feedback").text(igLang === "en" ? "Instagram is temporarily unavailable. Please use the profile link." : "Instagram временно недоступен. Откройте профиль по ссылке.");
				$btn.removeAttr('disabled').text(igLang === "en" ? "Show more" : "Показать ещё");
			}
		});
	});

	// Instagram Modal Feed functionality
	var igLoadingMore = false;

	// Render a single post HTML
	function escapeIgText(value) { return String(value || "").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;").replace(/'/g,"&#39;"); }
	function renderIgModalPost(post) {
		var isVideo = post.media_type === 'VIDEO' && post.video_url;
		var mediaHtml = isVideo
			? '<video class="ig-post-video" controls poster="' + escapeIgText(post.media_url) + '"><source src="' + escapeIgText(post.video_url) + '" type="video/mp4"></video>'
			: '<img src="' + escapeIgText(post.media_url) + '" alt="Post">';

		var followText = (typeof igLang !== 'undefined' && igLang === 'en') ? 'Follow' : 'Подписаться';
		var viewOnIgText = (typeof igLang !== 'undefined' && igLang === 'en') ? 'View on Instagram' : 'Открыть в Instagram';

		var html = '<div class="ig-modal-post" data-id="' + escapeIgText(post.id) + '">';
		html += '  <div class="ig-modal-header">';
		html += '    <img src="/almaty-travel-review/assets/images/ig_profile.jpg" class="ig-modal-avatar" alt="Profile">';
		html += '    <div class="ig-modal-user-info">';
		html += '      <span class="ig-modal-username">kazakhstan_travel</span>';
		html += '    </div>';
		html += '    <a href="https://instagram.com/kazakhstan_travel" target="_blank" class="ig-modal-follow-btn">' + followText + '</a>';
		html += '  </div>';
		html += '  <div class="ig-modal-media">' + mediaHtml + '</div>';
		html += '  <div class="ig-modal-content">';
		html += '    <div class="ig-modal-caption">';
		html += '      <span class="ig-modal-caption-user">kazakhstan_travel</span> ';
		html += escapeIgText(post.caption).replace(/\n/g,"<br>");
		html += '    </div>';
		html += '    <div class="ig-modal-date">' + escapeIgText(post.date) + '</div>';
		html += '    <a href="' + escapeIgText(post.permalink) + '" target="_blank" class="ig-modal-link">' + viewOnIgText + '</a>';
		html += '  </div>';
		html += '</div>';
		return html;
	}

	// Render all posts and open modal
	function openIgModalFeed(clickedPostId) {
		if (typeof igPostsData === 'undefined' || !igPostsData.length) return;

		var $container = $('#ig-modal-feed-container');
		$container.empty();

		// Find clicked post index
		var clickedIndex = 0;
		for (var i = 0; i < igPostsData.length; i++) {
			$container.append(renderIgModalPost(igPostsData[i]));
			if (igPostsData[i].id === clickedPostId) {
				clickedIndex = i;
			}
		}

		// Show modal
		$('#ig-modal-overlay').addClass('active');
		$('body').css('overflow', 'hidden');

		// Scroll to clicked post
		setTimeout(function () {
			var $clickedPost = $container.find('.ig-modal-post').eq(clickedIndex);
			if ($clickedPost.length && clickedIndex > 0) {
				// Calculate scroll position
				var scrollTo = 0;
				$container.find('.ig-modal-post').each(function (idx) {
					if (idx < clickedIndex) {
						scrollTo += $(this).outerHeight(true);
					}
				});
				$container.scrollTop(scrollTo);
			}
		}, 100);

		// Bind scroll event directly to container
		$container.unbind('scroll').scroll(function () {
			var el = this;
			var scrollTop = el.scrollTop;
			var scrollHeight = el.scrollHeight;
			var clientHeight = el.clientHeight;

			// Near bottom - load more
			if (scrollHeight - scrollTop - clientHeight < 300) {
				loadMoreIgPosts();
			}
		});
	}

	// Click on grid item to open modal
	$('.ig-modal-trigger').live('click', function (e) {
		e.preventDefault();
		var postId = $(this).attr('data-id');

		// Fallback to permalink match if no id
		if (!postId && typeof igPostsData !== 'undefined') {
			var permalink = $(this).attr('data-permalink');
			for (var i = 0; i < igPostsData.length; i++) {
				if (igPostsData[i].permalink === permalink) {
					postId = igPostsData[i].id;
					break;
				}
			}
		}

		openIgModalFeed(postId);
	});

	function loadMoreIgPosts() {
		if (igLoadingMore) return;
		if (typeof igNextCursor === 'undefined' || !igNextCursor) return;

		igLoadingMore = true;
		$('#ig-modal-loading').show();

		$.ajax({
			url: '/ajax.php',
			type: 'POST',
            timeout: 12000,
			data: { go: 'load_more_instagram', after: igNextCursor, lang: (typeof igLang !== 'undefined' ? igLang : 'ru') },
			success: function (resp) {
				try {
					var data = (typeof resp === 'string') ? JSON.parse(resp) : resp;
if(!data || typeof data !== 'object') throw new Error('Invalid feed response');

					if(data.error){$("#ig-feedback").text(igLang === "en" ? "Instagram is temporarily unavailable. Please use the profile link." : "Instagram временно недоступен. Откройте профиль по ссылке.");igNextCursor=null;}
					if (data.posts && data.posts.length) {
						var $container = $('#ig-modal-feed-container');
						for (var i = 0; i < data.posts.length; i++) {
							var exists=false;for(var k=0;k<igPostsData.length;k++)if(igPostsData[k].id===data.posts[i].id)exists=true;if(!exists){igPostsData.push(data.posts[i]);$container.append(renderIgModalPost(data.posts[i]));}
						}
					}

					igNextCursor = data.next_cursor || null;
				} catch (e) {
					console.error('Error parsing more posts');$("#ig-feedback").text(igLang === "en" ? "Instagram is temporarily unavailable. Please use the profile link." : "Instagram временно недоступен. Откройте профиль по ссылке.");
				}

				$('#ig-modal-loading').hide();
				igLoadingMore = false;
			},
			error: function () {
$("#ig-feedback").text(igLang === "en" ? "Instagram is temporarily unavailable. Please use the profile link." : "Instagram временно недоступен. Откройте профиль по ссылке.");
				$('#ig-modal-loading').hide();
				igLoadingMore = false;
			}
		});
	}

	// Close modal on close button click
	$('#ig-modal-close').live('click', function () {
		closeIgModal();
	});

	// Close modal on overlay click
	$('#ig-modal-overlay').live('click', function (e) {
		if ($(e.target).is('#ig-modal-overlay')) {
			closeIgModal();
		}
	});

	// Close modal on Escape key
	$(document).keydown(function (e) {
		if (e.keyCode === 27 && $('#ig-modal-overlay').hasClass('active')) {
			closeIgModal();
		}
	});

	function closeIgModal() {
		$('#ig-modal-overlay').removeClass('active');
		$('body').css('overflow', '');
		// Stop all videos
		$('#ig-modal-feed-container video').each(function () {
			this.pause();
			this.currentTime = 0;
		});
	}
});