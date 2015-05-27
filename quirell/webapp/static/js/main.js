$(document).ready(function(){
    // Image Upload Section
    $('.cloudinary-fileupload').bind('fileuploadstart', function(e, data) {
        $('progress').css("display", "inline-block")
    })
    $('.cloudinary-fileupload').bind('fileuploadprogress', function(e, data) {
        $('progress').attr("value", Math.round((data.loaded * 100) / data.total))
    })
    $('.cloudinary-fileupload').bind('fileuploadfail', function(e, data) {
        $('.upload_status').text(data)
    })
    $('.cloudinary-fileupload').bind('cloudinarydone', function(e, data) {
        $('.img_preview').attr("src", data.result.url)
        $('progress').css("display", "none")
        $('.upload_status').text('Upload Complete!')
        ajax_post($('#profile_edit_form'))
        // hide progress bar
    })

    // form AJAX section
    var ajax_post = function($form) {
        $.ajax({
            url: $form.attr("action"),
            data: $form.serialize(),
            type: $form.attr("method"),
        })
    }
    // do an AJAX post request if any of the profile edit fields besides
    // file inputs change
    $('#profile_edit_form input[type!="file"]').on("change", function() {
        ajax_post($('#profile_edit_form'))
    })
    // overide profile edit submission to use AJAX
    $('#profile_edit_form').on("submit", function(event) {
        ajax_post($(this))
        event.preventDefault()
    })
})
