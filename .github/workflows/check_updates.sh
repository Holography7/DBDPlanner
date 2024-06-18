# DO NOT RUN THIS SCRIPT! IT'S USING IN GITHUB ACTIONS FOR DEVELOPING!
pip_list_output="$(pip list --outdated --exclude pydantic-core)"
if [[ -n $pip_list_output ]]
then
    printf -- "%s\n" "$pip_list_output"
    exit 1
else
    printf -- "All packages is up to date.\n"
fi
