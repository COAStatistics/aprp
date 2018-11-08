var socialWallHelper = {

    init: function(){
        $(window).on('scroll', loadOnScroll);
        $('.modal').on('click', '#btn-post-cancel', function() {
            $('#dialog-form-post').modal('toggle');
        })
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", $.cookie('csrftoken'))
                }
            }
        });
        // Init post masonry
        $grid = $('.grid').masonry({
            itemSelector: '.grid-item',
            columWidth: '.grid-sizer',
            percentPosition: true,
        });

        this.initScrollToTop();
        this.initSearchBar();
        this.initNewPostBtn();
        this.initPost($grid);
        this.infinitePost();
    },


    infinitePost: function() {
        // -------------------- Infinite Scroll Start --------------------
        var pageNum = 1;
        var hasNextPage = true;
        keyword = $('#search-area').data('keyword');
        value = $('#search-area').data('value');

        while( $(window).height() + $(window).scrollTop() > $('.grid').height()-300 && hasNextPage === true ) {
            hasNextPage = socialWallHelper.requestPost({
                page: pageNum,
                keyword: keyword,
                value: value,
            });
            pageNum = pageNum + 1;
        }

        $(window).on('scroll', function() {
            if ( $(window).height() + $(window).scrollTop() > $('.grid').height()-300 && hasNextPage === true) {
                hasNextPage = socialWallHelper.requestPost({
                    page: pageNum,
                    keyword: keyword,
                    value: value,
                });
                pageNum = pageNum + 1;
            } else {
                return false;
            }
        });
        // -------------------- Infinite Scroll Start --------------------
    },


    requestPost: function(data) {
        var url = $grid.attr('data-infinite');
        $.ajax({
            type: 'get',
            url: url,
            contentType: 'application/json',
            async: false,
            data: data,
            success: function(data) {
                if(data['api']['next'] === null) {
                    hasNextPage = false;
                } else if(data['api']['count'] <= 5) {
                    hasNextPage = false;
                } else {
                    hasNextPage = true;
                }
                $item = $(data['html']);
                $('.grid').append($item).masonry('appended', $item).masonry('reloadItems').masonry();
                socialWallHelper.initPost($item);
                $grid.masonry();
            },
            statusCode: {
                404: function(xhr, statusText, err) {
                    hasNextPage = false;
                }
            }
        });
        return hasNextPage;
    },


    initScrollToTop: function() {
        if($(window).scrollTop() >= $(window).height()) {
            $('#btn-scroll-top').parents('.tool-div').fadeIn(500);
        } else {
            $('#btn-scroll-top').parents('.tool-div').fadeOut(500);
        }
        $('#btn-scroll-top').on('click', function(e) {
            e.preventDefault();
            $('html').animate({scrollTop: 0}, 'slow');
        });
    },


    initSearchBar: function() {
        $('.search-panel .dropdown-menu').find('a').click(function(e) {
            e.preventDefault();
            var concept = $(this).text();
            var data_type = $(this).attr('data-type');
            $('.search-panel span#search_concept').text(concept);
            $('.input-group #search_param').val(data_type);
            $('.search-text').attr('placeholder', $('.search-text').attr('data-hint'));
        });

        $('.search-btn').on('click', function() {
            $item = $(this).parents('.search-area');
            url = $item.find('#search_concept').attr('url');
            text = $item.find('.search-text').val();
            if($item.find('#search_concept').text() === gettext('Filter by')) {
                $item.find('#search_concept').text(gettext('All'));
            }
            key = $('.input-group #search_param').val();
            $('#search-area').data('keyword', key);
            $('#search-area').data('value', text);
            $grid.html('<div class="grid-sizer col-md-6 col-xs-12"></div>');
            $grid.masonry('reloadItems').masonry();
            $(window).unbind('scroll');
            $(window).on('scroll', loadOnScroll);
            socialWallHelper.infinitePost();
        });

        $('.search-text').keyup(function(e) {
            if(e.keyCode == 13) {
                $item = $(this).parents('.search-area');
                url = $item.find('#search_concept').attr('url');
                text = $item.find('.search-text').val();
                if($item.find('#search_concept').text() === gettext('Filter by')) {
                    $item.find('#search_concept').text(gettext('All'));
                }
                key = $('.input-group #search_param').val();
                $('#search-area').data('keyword', key);
                $('#search-area').data('value', text);
                $grid.html('<div class="grid-sizer col-md-6 col-xs-12"></div>');
                $grid.masonry('reloadItems').masonry();
                $(window).unbind('scroll');
                $(window).on('scroll', loadOnScroll);
                socialWallHelper.infinitePost();
            }
        });
    },


    initNewPostBtn: function() {
        // -------------------- create post start --------------------
        // $posts.find('#btn-newpost').click(function() {
        $('.row').on('click', '#btn-newpost', function(e) {
            e.preventDefault();
            $('#socialwall-title-new').show();
            $('#socialwall-title-edit').hide();
            form = $('#form-post');
            url = form.attr('action');

            $.ajax({
                type: 'get',
                url: url,
                success: function (data) {
                    // console.log(data);
                    $('#modal-body').html(data);
                    $('#dialog-form-post').modal('show');
                    socialWallHelper.initFormNew();
                }
            });
        });

        // -------------------- create post end --------------------

    },


    initFormNew: function() {
        $('form').submit(function (e) {

            e.preventDefault();

            url = $(this).attr('api');

            data = $(this).formcontrol().data();
            hasFile = false;

            try {
                $('#id_file')[0].files[0].name;
                form = new FormData();
                $.each(data, function(key, val) {
                    form.append(key, val);
                });
                form.append('file', $('#id_file')[0].files[0])
                hasFile = true;
            } catch (e) {}

            if(hasFile) {
                // console.log('has file')
                $.ajax({
                    type: 'post',
                    url: url,
                    data: form,
                    contentType: false,
                    processData: false,
                    success: function(data) {
                        $item = $(data['html']);
                        if($grid.children('.socialwall-nodata').length > 0) {
                            $grid.html('');
                        }
                        $grid.prepend($item).masonry('prepended', $item);
                        $('#dialog-form-post').modal('hide');
                        socialWallHelper.initPost($item);
                    }
                }).fail(function (jqXHR, textStatus, errorThrown) {
                    if(jqXHR.responseJSON){
                        $('form').formcontrol().validate(jqXHR.responseJSON);
                    }else{
                        console.log(jqXHR);
                    }
                });
            } else {
                // console.log('no file')
                $.ajax({
                    type: 'post',
                    url: url,
                    data: data,
                    success: function(data) {
                        $item = $(data['html']);
                        if($grid.children('.socialwall-nodata').length > 0) {
                            $grid.html('');
                        }
                        $grid.prepend($item).masonry('prepended', $item);
                        $('#dialog-form-post').modal('hide');
                        socialWallHelper.initPost($item);
                    }
                }).fail(function (jqXHR, textStatus, errorThrown) {
                    if(jqXHR.responseJSON){
                        $('form').formcontrol().validate(jqXHR.responseJSON);
                    }else{
                        console.log(jqXHR);
                    }
                });
            }
        });
    },


    initEditPostBtn: function() {
        $('form').submit(function (e) {
            e.preventDefault();

            id = $(this).attr('data-id');
            url = $(this).attr('api') + id;
            $div = $('#div-' + id)

            data = $(this).formcontrol().data();
            hasFile = false;

            try {
                $('#id_file')[0].files[0].name;
                form = new FormData();
                $.each(data, function(key, val) {
                    form.append(key, val);
                });
                form.append('file', $('#id_file')[0].files[0])
                hasFile = true;
            } catch (e) {}

            if(hasFile) {
                // console.log('has file')
                $.ajax({
                    type: 'patch',
                    url: url,
                    data: form,
                    contentType: false,
                    processData: false,
                    success: function(data) {
                        $item = $(data['html']);
                        socialWallHelper.initPost($item);
                        $div.find('.post-edit-area').remove();
                        $div.find('.post-update').prepend($item);
                        $grid.masonry('layout');
                        $('#dialog-form-post').modal('hide');
                    }
                }).fail(function (jqXHR, textStatus, errorThrown) {
                    if(jqXHR.responseJSON){
                        $('form').formcontrol().validate(jqXHR.responseJSON);
                    }else{
                        console.log(jqXHR);
                    }
                });
            } else {
                // console.log('no file')
                $.ajax({
                    type: 'patch',
                    url: url,
                    data: data,
                    success: function(data) {
                        $item = $(data['html']);
                        socialWallHelper.initPost($item);
                        $div.find('.post-edit-area').remove();
                        $div.find('.post-update').prepend($item);
                        $grid.masonry('layout');
                        $('#dialog-form-post').modal('hide');
                    }
                }).fail(function (jqXHR, textStatus, errorThrown) {
                    if(jqXHR.responseJSON){
                        $('form').formcontrol().validate(jqXHR.responseJSON);
                    }else{
                        console.log(jqXHR);
                    }
                });
            }
        });
    },


    initPost: function($item){

        // -------------------- edit post start --------------------
        $item.find('.post-edit').on('click', function() {
            $('#socialwall-title-new').hide();
            $('#socialwall-title-edit').show();
            id = $(this).attr('data-id');
            url = $(this).attr('api') + id;
            $.ajax({
                type: 'get',
                url: url,
                success: function(data){
                    $('#modal-body').html(data['html']);
                    $('#dialog-form-post').modal('show');
                    socialWallHelper.initEditPostBtn();
                }
            });
        });
        // -------------------- edit post end --------------------

        // -------------------- delete post start --------------------
        $item.find('.post-delete').on('click', function () {
            $item = $(this);
            BootstrapDialog.confirm({
                title: gettext('Delete Post'),
                message: gettext('Are you sure you want to delete this post?'),
                type: BootstrapDialog.TYPE_DANGER,
                btnOKLabel: gettext('Delete'),
                btnCancelLabel: gettext('Cancel'),
                callback: function(result){
                    if(result) {
                        id = $item.attr('data-id');
                        url = $item.attr('api');
                        $post = $('#span-' + id).parent();
                        $.ajax({
                            type: 'DELETE',
                            url: url + id,
                            success: function() {
                                $grid.masonry('remove', $post).masonry('layout');
                            }
                        });
                    }
                }
            });
        });
        // -------------------- delete post end --------------------

        // -------------------- hide post start --------------------
        $item.find('.post-hide').on('click', function () {
            id = $(this).attr('data-id');
            $post = $('#span-' + id).parent();
            $grid.masonry('remove', $post).masonry('layout');
        });
        // -------------------- hide post end --------------------

        // -------------------- reply tag name start --------------------
        $item.find('.socialwall-btn-reply').on('click', function() {
            $parent = $(this).parents('.message');
            name = $parent.find('a').html().split('<small')[0].split(' ').join('');
            $parent = $(this).parents('.grid-item');
            $parent.find('#reply-text').val('@' + name + '  ');
            $parent.find('#reply-text').focus();
            // console.log(name);
        });
        // -------------------- reply tag name end --------------------

        // -------------------- reply new start --------------------
        $item.find('.form-control.input-xs.socialwall-reply-text').keyup(function (e) {
            if(e.keyCode == 13) {
                id = $(this).attr('data-id');
                url = $(this).attr('api');
                csrftoken = $(this).attr('data-token');
                text = $(this).val();
                $reply = $(this);
                $.ajax({
                    type: 'post',
                    url: url,
                    async: false,
                    data: {
                        csrfmiddlewaretoken: csrftoken,
                        'object_id': id,
                        'content': text,
                    },
                    success: function(data) {
                        $item = $(data);
                        socialWallHelper.initPost($item);
                        $reply.parents(".socialwall-reply").before($item);
                        text = $item.find('.reply-origin').html();
                        text = text.replace(/@(\S+)(\s|$)/g, '<mark class="label bg-color-blue">$1</mark> ');
                        $item.find('.reply-origin').html(text);
                        $reply.val('');
                        $grid.masonry();
                    }
                });
            }
        });

        $item.find('.btn-reply').on('click', function() {
            id = $(this).parents('.socialwall-reply-text').find('.socialwall-reply-text').attr('data-id');
            url = $(this).parents('.socialwall-reply-text').find('.socialwall-reply-text').attr('api');
            csrftoken = $(this).parents('.socialwall-reply-text').find('.socialwall-reply-text').attr('data-token');
            text = $(this).parents('.socialwall-reply-text').find('.socialwall-reply-text').val();
            $reply = $(this).parents('.socialwall-reply-text').find('.socialwall-reply-text');
            $.ajax({
                type: 'post',
                url: url,
                async: false,
                data: {
                    csrfmiddlewaretoken: csrftoken,
                    'object_id': id,
                    'content': text,
                },
                success: function(data) {
                    $item = $(data);
                    socialWallHelper.initPost($item);
                    $reply.parents(".socialwall-reply").before($item);
                    text = $item.find('.reply-origin').html();
                    text = text.replace(/@(\S+)(\s|$)/g, '<mark class="label bg-color-blue">$1</mark> ');
                    $item.find('.reply-origin').html(text);
                    $reply.val('');
                    $grid.masonry();
                }
            });
        });
        // -------------------- reply new end --------------------

        // -------------------- reply delete start --------------------
        $item.find('.reply-delete').on('click', function() {
            $item = $(this);
            BootstrapDialog.confirm({
                title: gettext('Delete Comment'),
                message: gettext('Are you sure you want to delete this comment?'),
                type: BootstrapDialog.TYPE_DANGER,
                btnOKLabel: gettext('Delete'),
                btnCancelLabel: gettext('Cancel'),
                callback: function(result){
                    if(result) {
                        id = $item.attr('data-id');
                        url = $item.attr('api');
                        $post = $('#span-' + id).parent();
                        $.ajax({
                            type: 'DELETE',
                            url: url + id,
                            success: function() {
                                $item.parents('.socialwall-reply').remove();
                                $grid.masonry();
                            }
                        });
                    }
                }
            });
        });
        // -------------------- reply delete end --------------------

        // -------------------- reply edit start --------------------
        $item.find('.reply-edit').on('click', function() {
            id = $(this).attr('data-id');
            url = $(this).attr('api');
            $reply = $(this).parents('.socialwall-reply');
            $reply.find('.comment').hide();
            $reply.find('.comment-edit').show();
            origin = $reply.find('.reply-origin').html();
            origin = origin.replace(/<mark class="label bg-color-blue">(\S+)<\/mark>/g, '@$1 ');
            $edittext = $reply.find('#reply-edit');
            $grid.masonry();
            $edittext.val(origin);
            $edittext.focus();

            $edittext.keyup(function(e) {
                if(e.keyCode == 13) {
                    data = $edittext.val();
                    $.ajax({
                        type: 'patch',
                        url: url + id,
                        async: false,
                        data: {
                            'content': data,
                        },
                        success: function(data) {
                            $reply.find('.comment').show();
                            $reply.find('.comment-edit').hide();
                            $reply.html($reply.html());
                            text = data['content'];
                            text = text.replace(/@(\S+)(\s|$)/g, '<mark class="label bg-color-blue">$1</mark> ');
                            $reply.find('.reply-origin').html(text);
                            socialWallHelper.initPost($reply);
                            $grid.masonry();
                            return;
                        }
                    }).fail(function() {
                        $reply.find('.comment').show();
                        $reply.find('.comment-edit').hide();
                    });
                }
            })

            $edittext.focusout(function(e) {
                data = $edittext.val();
                $.ajax({
                    type: 'patch',
                    url: url + id,
                    async: false,
                    data: {
                        'content': data,
                    },
                    success: function(data) {
                        $reply.find('.comment').show();
                        $reply.find('.comment-edit').hide();
                        $reply.html($reply.html());
                        text = data['content'];
                        text = text.replace(/@(\S+)(\s|$)/g, '<mark class="label bg-color-blue">$1</mark> ');
                        $reply.find('.reply-origin').html(text);
                        socialWallHelper.initPost($reply);
                        $grid.masonry();
                    }
                }).fail(function() {
                    $reply.find('.comment').show();
                    $reply.find('.comment-edit').hide();
                });
            });
        });
        // -------------------- reply edit end --------------------

        // -------------------- Search author start --------------------
        $item.find('a.username').on('click', function() {
            concept = gettext('Author');
            data_type = "Author";
            $('.search-panel span#search_concept').text(concept);
            $('.input-group #search_param').val(data_type);
            $('.search-text').attr('placeholder', $('.search-text').attr('data-hint'));
            $searchbar = $('.search-area');
            text = $(this).text();
            $searchbar.find('.search-text').val(text);
            url = $searchbar.find('#search_concept').attr('url');
            key = $('.input-group #search_param').val();
            $('#search-area').data('keyword', key);
            $('#search-area').data('value', text);
            $grid.html('<div class="grid-sizer col-md-6 col-xs-12"></div>');
            $grid.masonry('reloadItems').masonry();
            $(window).unbind('scroll');
            $(window).on('scroll', loadOnScroll);
            socialWallHelper.infinitePost();
            $('html').animate({scrollTop: 0}, 'slow');
        });
        // -------------------- Search author end --------------------

        // -------------------- Img Resize Start --------------------
        $item.find('img').on('load', function() {
            $grid.masonry();
        });
        $('.reply-origin').each(function() { $(this).html($(this).html().replace(/@(\S+)(\s|$)/g, '<mark class="label bg-color-blue">$1</mark> '))  });
        // -------------------- Img Resize end --------------------

        // -------------------- Read More Start --------------------
        // $('.read-more').readMore()
        //
        // $('#row-post').on('click', 'button', function () {
        //   $grid.masonry('layout')
        //   console.log('read more ok, reloaditems ok')
        // })
        // -------------------- Read More End --------------------

    },
}

// var initPost = function($posts) {
//
// }

// -------------------- like thumb start --------------------
// $('.toggle-like').on('click', '.reply-like', function() {
//   $(this).children('i').removeClass('fa-thumbs-o-up')
//   $(this).children('i').addClass('fa-thumbs-up')
//   $(this).removeClass('reply-like')
//   $(this).addClass('reply-like-up')
// })
//
// $('.toggle-like').on('click', '.reply-like-up', function() {
//   $(this).children('i').removeClass('fa-thumbs-up')
//   $(this).children('i').addClass('fa-thumbs-o-up')
//   $(this).removeClass('reply-like-up')
//   $(this).addClass('reply-like')
// })
// -------------------- like thumb start --------------------



var loadOnScroll = function() {
// // $(window).bind('scroll', function() {
    if($(window).scrollTop() >= $(window).height()) {
        $('#btn-scroll-top').parents('.tool-div').fadeIn(500);
    } else {
        $('#btn-scroll-top').parents('.tool-div').fadeOut(500);
    }
// // });
};


// solve the problem ckeditor with modal can't focus on ckeditor's modal like insert img
$.fn.modal.Constructor.prototype.enforceFocus = function () {
    var $modalElement = this.$element;
    $(document).on('focusin.modal',
    function (e) {
        var $parent = $(e.target.parentNode);
        if ($modalElement[0] !== e.target &&
            !$modalElement.has(e.target).length &&
            !$parent.hasClass('cke_dialog_ui_input_select') &&
            !$parent.hasClass('cke_dialog_ui_input_text')) {
            $modalElement.focus();
        }
    });
};
