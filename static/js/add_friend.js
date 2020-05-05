async function addFriend(friendButton) {
    let email = friendButton.dataset.email;
    let addingFriend = friendButton.innerText === "Add Friend";

    if (addingFriend) {
        friendButton.innerText = "Remove Friend";
        friendButton.classList.remove("add_friend");
        friendButton.classList.add("remove_friend");
    } else {
        friendButton.innerText = "Add Friend";
        friendButton.classList.remove("remove_friend");
        friendButton.classList.add("add_friend");
    }

    let data = { email };

    let endpoint = addingFriend ? "/addFriend" : "/removeFriend";

    await fetch(endpoint, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
    });
}
