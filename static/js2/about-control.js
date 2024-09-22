function postsaran() {
    let username = $("#username").val();
    let message = $("#message").val();
    $.ajax({
      type: "POST",
      url: "/post_saran",
      data: {
        username_give: username,
        message_give: message,
      },
      success: function (response) {
        if (response["result"] === "success") {
          alert(response["msg"]);
          $("#username").val("");
          $("#message").val("");
        }
      },
    });
  }