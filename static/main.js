$('document').ready(()=> {

    $("#book-search").select();

    // $("#mostra").on("click", (event)=>{
    //     event.preventDefault()
    //     $.ajax({
    //         data : JSON.stringify({ "count" : 5 }),
    //         url : "/",
    //         contentType : "application/json",
    //         type : "post"
    //     }).done((response)=>{
    //         location.reload()
    //     })
    // })

    $("button").on("click", (event)=>{
        isbn = event.target.id;
        $.ajax({
            data : JSON.stringify({
                "isbn" : isbn
            }),
            type: "post",
            contentType: 'application/json',
            url: "/deleteBook"
        }).done((response)=>{
            event.target.parentElement.remove()
        })
    });

    $("input[type='radio']").on("change", (event)=>{
        $.ajax(
            {
                data: JSON.stringify({
                    "isbn" : event.target.name,
                    "state" : event.target.value
                }),
                type: "post",
                contentType: 'application/json',
                url: "/changeState",
            }
        )
    })
});