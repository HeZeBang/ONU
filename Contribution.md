# Contribution Guidelines

Welcome to contribute to `ONU!` Follow the steps below:

1. Fork this repository
   Click the "Fork" button in the upper right corner of the project page to create a fork under your GitHub account.

2. Clone the repository locally

   ```bash
   git clone https://github.com/HeZeBang/ONU.git
   ```

3. Create a branch

   ```bash
   git checkout -b feature/your-feature    # add a feature
   git checkout -b bugfix/your-patch       # fix a bug
   ```

4. Make changes
   Make changes on your local branch, ensuring compliance with the project's code standards.

5. Run tests
   After the changes, make sure to run the project's tests to ensure your changes haven't introduced new issues.

6. Commit changes

   ```bash
   git add .
   git commit -m "Add your commit message here"
   ```

7. Push changes

   ```bash
   git push origin feature/your-feature
   ```

8. Submit a Pull Request

   On the GitHub page, select the "New Pull Request" button, choose your branch, and submit the Pull Request.

## Code Standards

Ensure your code adheres to the project's coding standards.

| Naming Convention | Applicable Types | Example           |
| ------------------ | ----------------- | ------------------ |
| Snake Case         | Global variables, functions;<br>Variables inherited from the ONU module | `global_variable` |
| Upper Snake Case   | Constants          | `CONST_VARIABLE`   |
| Camel Case         | Local variables    | `myVariable`      |
| Pascal Case        | Class names;<br>Interface names | `MyClass`          |

## Commit Message Guidelines

Use clear, concise commit messages describing what your changes are. If applicable, follow the Conventional Commits specification.

## License

Ensure your changes comply with the project's license.

`ONU!` is based on the MIT license.

## Contact Information

If you have any questions or need assistance, please raise an issue on GitHub or send an email to zambar@shanghaitech.edu.cn.

## Acknowledgments

Thank you for contributing to the project!