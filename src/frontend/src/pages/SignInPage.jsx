import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { SignInForm } from '@/components/authentication/SignInForm';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';

export function SignInPage() {
  return (
    <main className="mx-auto grid min-h-svh w-full place-items-center p-6">
      <Card className="w-full max-w-lg">
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl">Sign in</CardTitle>
          <CardDescription>Choose your preferred sign in method</CardDescription>
        </CardHeader>

        <CardContent className="grid gap-4">
          <Button type="button" variant="outline" className="w-full">
            Continue with Google
          </Button>

          <div className="relative">
            <div className="absolute inset-0 flex items-center" aria-hidden="true">
              <Separator />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-background px-2 text-muted-foreground">
                Or continue with
              </span>
            </div>
          </div>

          <SignInForm />
        </CardContent>

        <CardFooter className="flex flex-wrap items-center justify-between gap-2">
          <div className="text-sm text-muted-foreground">
            <span className="mr-1 hidden sm:inline-block">
              Don&apos;t have an account?
            </span>
            <Link
              aria-label="Sign up"
              to="/signup"
              className="text-primary underline-offset-4 transition-colors hover:underline"
            >
              Sign up
            </Link>
          </div>
          <Link
            aria-label="Reset password"
            to="/signin/reset-password"
            className="text-sm text-primary underline-offset-4 transition-colors hover:underline"
          >
            Reset password
          </Link>
        </CardFooter>
      </Card>
    </main>
  );
}