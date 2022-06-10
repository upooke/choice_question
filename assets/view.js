if (CTFd._internal.challenge) {
  var challenge = CTFd._internal.challenge;
} else {
  var challenge = window.challenge;
}

if (CTFd.lib.$) {
  $ = CTFd.lib.$;
}

function htmlDecode(value) {
  return $("<textarea/>")
    .html(value)
    .text();
}

challenge.data = undefined;

challenge.renderer = CTFd.lib.markdown();

challenge.preRender = function() {};

challenge.render = function(markdown) {
  challenge.renderer.block.ruler.before(
    "list",
    "multiple-choice",
    function replace(state, startLine, endLine, silent) {
      var marker,
        cnt,
        ch,
        token,
        pos = state.bMarks[startLine] + state.tShift[startLine],
        max = state.eMarks[startLine];

      var nextLine = startLine + 1;
      var content = state
        .getLines(startLine, nextLine, state.blkIndent, false)
        .trim();

      if (!(content.startsWith("* ()") || content.startsWith("* (X)"))) {
        return false;
      }

      if (content.startsWith("* ()")) {
        var text = content.substr(5); // Cut out the * () part
        if (text.startsWith(" ")) {
          text = text.substr(1);
        }
      } else if (content.startsWith("* (X)")) {
        var text = content.substr(6); // Cut out the * (X) part
        if (text.startsWith(" ")) {
          text = text.substr(1);
        }
      }
      state.line = nextLine;

      token = state.push("choice_div_open", "div", 1);
      token.attrPush(["class", "form-check ctfd-multiple-choice-item"]);

      token = state.push("choice_label_open", "label", 1);

      token = state.push("choice_input", "input", 0);
      token.attrPush(["type", "radio"]);
      token.attrPush(["name", "answer"]);
      token.attrPush(["value", text]);

      token = state.push("choice_text_open", "span", 1);

      token = state.push("inline", "", 0);
      token.content = text;
      token.map = [startLine, state.line];
      token.children = [];

      token = state.push("choice_text_close", "span", -1);

      token = state.push("choice_label_close", "label", -1);

      token = state.push("choice_div_close", "div", -1);

      return true;
    }
  );

  return challenge.renderer.render(markdown);
};

challenge.postRender = function() {
  let content = CTFd.lib
    .$(".challenge-desc")
    .html()
    .trim();

  // Without doing this you don't render the actual HTML content
  let decodedContent = htmlDecode(content);
  let rendered = challenge.render(decodedContent);
  CTFd.lib.$(".challenge-desc").html(rendered);
};

challenge.submit = function(preview) {
  var challenge_id = parseInt(CTFd.lib.$("#challenge-id").val());

  var list = CTFd.lib.$(".challenge-desc")[0];
  var radio = CTFd.lib
    .$(list)
    .find(".ctfd-multiple-choice-item input[type=radio]:checked")[0];
  var submission = CTFd.lib.$(radio).val();

  // Handle no selection case
  if (Boolean(submission) === false) {
    submission = "";
  }

  var body = {
    challenge_id: challenge_id,
    submission: submission
  };
  var params = {};
  if (preview) {
    params["preview"] = true;
  }

  return CTFd.api.post_challenge_attempt(params, body).then(function(response) {
    if (response.status === 429) {
      // User was ratelimited but process response
      return response;
    }
    if (response.status === 403) {
      // User is not logged in or CTF is paused.
      return response;
    }
    return response;
  });
};
