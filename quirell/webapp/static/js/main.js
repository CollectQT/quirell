$(document).ready(function(){
    // Image Upload Section
    $('.cloudinary-fileupload').bind('fileuploadstart', function(e, data) {
        // progress bar
    })
    $('.cloudinary-fileupload').bind('fileuploadfail', function(e, data) {
        $('.upload_status').text(data)
    })
    $('.cloudinary-fileupload').bind('cloudinarydone', function(e, data)
    {
        $('.img_preview').attr("src", data.result.url)
        $('.upload_status').text('Upload Complete!')
        // hide progress bar
    })

    // form AJAX section
    $('#profile_edit_form').on("change", function() {
        $.ajax({
            url: $(this).attr("action"),
            data: $(this).serialize(),
            type: $(this).attr("method"),
            success: function(response) {
                console.log(response)
            }
        })
    })
})
