const puppeteer = require('puppeteer');
​
function goToIteuns() {
	try {
		(async () => {
			const browser = await puppeteer.launch({
				headless : false,
				defaultViewport: {
					width: 1600,
					height: 900
				}
			});
			const page = await browser.newPage();
			await page.goto('https://video.google.com');
			await page.type('input#lst-ib.lst', 'tornado', {delay:50});
			page.keyboard.press('Enter');
			await page.waitForSelector('div#resultStats');
			const hrefs1 = await page.evaluate(
				() => Array.from(
				  document.querySelectorAll('a[href]'),
				  a => a.getAttribute('href')
				)
			  );
			  let filteredArr = hrefs1.filter((link)=>{
				  return (link.indexOf('youtube.com') >= 0); 
			  })
			  return console.log(filteredArr[0]);
		})();
	} catch (err) {
		console.error(err);
	}
}
​
return goToIteuns();