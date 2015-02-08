// whenever a picture is set for uploading, load it into preview box(es)
$('.img_upload').change(function(){
    $('.img_preview').attr('src', window.URL.createObjectURL(this.files[0]));
});
