CREATE TABLE IF NOT EXISTS Post (
    post_id INT GENERATED ALWAYS AS IDENTITY,
    post_time TIMESTAMP NOT NULL,
    title varchar(300) NOT NULL,
    PRIMARY KEY (post_id)
);

CREATE TABLE IF NOT EXISTS Post_keyword (
    post_keyword_id INT GENERATED ALWAYS AS IDENTITY,
    post_keyword VARCHAR(50) NOT NULL UNIQUE,
    PRIMARY KEY (post_keyword_id)
);

CREATE TABLE IF NOT EXISTS Keyword_in_post (
    post_id INT NOT NULL,
    post_keyword_id INT NOT NULL,
    FOREIGN KEY (post_id) REFERENCES Post(post_id),
    FOREIGN KEY (post_keyword_id) REFERENCES Post_keyword(post_keyword_id),
    UNIQUE (post_id, post_keyword_id)
);

CREATE TABLE IF NOT EXISTS Comment (
    comment_id INT GENERATED ALWAYS AS IDENTITY,
    comment_time TIMESTAMP NOT NULL,
    comment VARCHAR(10000) NOT NULL,
    score INT NOT NULL,
    sentiment FLOAT NOT NULL,
    post_id INT NOT NULL,
    FOREIGN KEY (post_id) REFERENCES Post(post_id),
    PRIMARY KEY (comment_id)
);

CREATE TABLE IF NOT EXISTS Comment_keyword (
    comment_keyword_id INT GENERATED ALWAYS AS IDENTITY,
    comment_keyword VARCHAR(50) NOT NULL UNIQUE,
    PRIMARY KEY (comment_keyword_id)
);

CREATE TABLE IF NOT EXISTS Keyword_in_comment (
    comment_id INT NOT NULL,
    comment_keyword_id INT NOT NULL,
    FOREIGN KEY (comment_id) REFERENCES Comment(comment_id),
    FOREIGN KEY (comment_keyword_id) REFERENCES Comment_keyword(comment_keyword_id),
    UNIQUE (comment_id, comment_keyword_id)
);