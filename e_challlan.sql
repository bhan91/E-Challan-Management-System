SELECT p.login_id, p.username, pd.officer_name
FROM Police p
JOIN Police_Details pd ON p.police_id = pd.police_id;
