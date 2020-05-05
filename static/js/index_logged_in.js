function setMovieList() {
    movies = movies.map((movie_name) => {
        return { title: movie_name };
    });

    $("#movie_select").selectize({
        maxItems: 1,
        maxOptions: 10,
        options: movies,
        labelField: "title",
        valueField: "title",
        searchField: "title",
        placeholder: "Search for a movie",
        onChange: (movie) => {
            window.location = "/movie?movie_name=" + encodeURIComponent(movie);
        },
    });
}
