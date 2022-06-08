    function api_call(input) {

        $.ajax({
            url: 'http://' + document.domain + '/infer',
            type: 'POST',
            contentType: 'application/json;charset=utf-8',
            data: JSON.stringify(input),
                success:function(res){
                    console.log(res)
                    console.log(0)

                },
                error:function (res) {
                    console.log(res);
                    console.log(1)
                },
            timeout: 20000 // sets timeout to 10 seconds
        });

    }

    $(function () {
        $('button').click(function () {
            var input = $("#input").val();
            if (input === "") {
                alert("请先输入文本");
            } else {
                api_call(input);
            }
        })});

    // $(function(){
    //     $('button').click(function (){$('.online_result').addClass("white")})
    //
    // })