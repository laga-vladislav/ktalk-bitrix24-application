<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<title>Quick start. Local server-side application with UI</title>
</head>
<body>
	<div id="auth-data">OAuth 2.0 data from REQUEST:
		<pre><?php
			print_r($_REQUEST);
			?>
		</pre>
	</div>
	<div id="name">
		<?php
		require_once (__DIR__.'/crestcurrent.php');

		//$result = CRest::call('user.current');
		$result = CRestCurrent::call('user.current');

		echo $result['result']['NAME'].' '.$result['result']['LAST_NAME'];
		?>
	</div>
</body>
</html>