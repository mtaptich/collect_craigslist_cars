<h1>Python Script to Scrap Craiglist Data</h1>

<h3>A few things about this package:</h3>
<ul>
	<li> You run everything from <code>tc2o.py</code> </li>
	<li> You must update the email information to email the csv results (scripts/email_csv.py)</li>
	<li> SearchVehicles variable represents the vehicles you are interested in. </li>
</ul>
</p>


<h3> Scraping Data </h3>
<p>
	<code>craigslist_cars.py</code> is the script that pulls car listings. The query function within this script looks like this:<br>
	<pre><code>query(city, limit, brand, model, minimum_price="2000", minimum_year="2006", ...
	maximum_odometer="180000", week_range=5 ,blacklist_titles=['salvage', 'rebuilt'])</code></pre>
</p>