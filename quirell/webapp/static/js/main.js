$(document).ready(function(){
    // Image Upload Section
    $('.cloudinary-fileupload').bind('cloudinarydone', function(e, data) {
        $('.img_preview').attr("src", data.result.url);
    });
    $('.cloudinary-fileupload').bind('fileuploadfail', function(e, data) {
        $('.upload_status').html(data);
        console.log('mew?');
    });
})
